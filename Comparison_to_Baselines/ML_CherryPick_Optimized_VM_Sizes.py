import os
import sys
import subprocess
import json
import logging
from botocore.exceptions import ClientError
import boto3
from StepFunction_util import *
import numpy as np
import sklearn.gaussian_process as gp
import random
from scipy.stats import norm
from scipy.optimize import minimize
import string
from datetime import datetime
import time

logger = logging.getLogger(__name__)
DAG_arn = ""
def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)

def minimized_function(params, DAG_arn):
    F1 = int(params[0])
    F2 = int(params[1])
    F3 = int(params[2])
    

    lambda_client = boto3.client('lambda')
    stepFunctions_client = boto3.client('stepfunctions')
    print(DAG_arn)
    step_controler = StepFunctionsStateMachine(stepFunctions_client, DAG_arn)
    # Extract all function arns from the DAG
    describe_out = step_controler.describe()
    j_def = json.loads(describe_out['definition'])
    describe_out_unrolled = recursive_items(j_def)
    function_arns = []
    for key, value in describe_out_unrolled:
        if(key == "Resource"):
            #print(key, value)
            function_arns.append(value)
    print("Identified the following functions in the DAG")
    print(function_arns)   

    for func_id in range(len(function_arns)):
        memSize = int(params[func_id])
        response = lambda_client.update_function_configuration(FunctionName=function_arns[func_id], MemorySize=int(memSize))
   
    letters = string.ascii_lowercase
    run_hash = ''.join(random.choice(letters) for i in range(10))
    run_name = "run_" + run_hash

    start_time = int(round(time.time() * 1000))
    run_arn = step_controler.start_run(run_name, { "bundle_size": 4, "key1": "300"})
    
    run_succeeded = False
    for i in range(200): # Busy loop until success or until 1000 seconds have elapsed
       arn_describtion = step_controler.describe_execution(run_arn)
       #print(arn_describtion)
	   
       print("+++++++++++++++++++++++++++++++++++++++++++")
       if(arn_describtion['status'] == 'SUCCEEDED'):
          run_succeeded = True
          break
       elif(arn_describtion['status'] == 'FAILED'):
          break
       else:
          print("still running!")	   
       time.sleep(5)

    if(run_succeeded == True):
       end_time = int(round(time.time() * 1000))
       diff = end_time - start_time
       print("testing params: " + str(params))
       print("E2E latency (ms): " + str(diff))
       return diff

    return 0 

def expected_improvement(x, gaussian_process, evaluated_loss, greater_is_better=False, n_params=1):
    """ expected_improvement
    Expected improvement acquisition function.
    Arguments:
    ----------
        x: array-like, shape = [n_samples, n_hyperparams]
            The point for which the expected improvement needs to be computed.
        gaussian_process: GaussianProcessRegressor object.
            Gaussian process trained on previously evaluated hyperparameters.
        evaluated_loss: Numpy array.
            Numpy array that contains the values off the loss function for the previously
            evaluated hyperparameters.
        greater_is_better: Boolean.
            Boolean flag that indicates whether the loss function is to be maximised or minimised.
        n_params: int.
            Dimension of the hyperparameter space.
    """

    x_to_predict = x.reshape(-1, n_params)

    mu, sigma = gaussian_process.predict(x_to_predict, return_std=True)

    if greater_is_better:
        loss_optimum = np.max(evaluated_loss)
    else:
        loss_optimum = np.min(evaluated_loss)

    scaling_factor = (-1) ** (not greater_is_better)

    # In case sigma equals zero
    with np.errstate(divide='ignore'):
        Z = scaling_factor * (mu - loss_optimum) / sigma
        expected_improvement = scaling_factor * (mu - loss_optimum) * norm.cdf(Z) + sigma * norm.pdf(Z)
        expected_improvement[sigma == 0.0] == 0.0

    return -1 * expected_improvement


def sample_next_hyperparameter(acquisition_func, gaussian_process, evaluated_loss, greater_is_better=False,
                               bounds=(0, 10), n_restarts=25):
    """ sample_next_hyperparameter
    Proposes the next hyperparameter to sample the loss function for.
    Arguments:
    ----------
        acquisition_func: function.
            Acquisition function to optimise.
        gaussian_process: GaussianProcessRegressor object.
            Gaussian process trained on previously evaluated hyperparameters.
        evaluated_loss: array-like, shape = [n_obs,]
            Numpy array that contains the values off the loss function for the previously
            evaluated hyperparameters.
        greater_is_better: Boolean.
            Boolean flag that indicates whether the loss function is to be maximised or minimised.
        bounds: Tuple.
            Bounds for the L-BFGS optimiser.
        n_restarts: integer.
            Number of times to run the minimiser with different starting points.
    """
    best_x = None
    best_acquisition_value = 1
    n_params = bounds.shape[0]

    for starting_point in np.random.uniform(bounds[:, 0], bounds[:, 1], size=(n_restarts, n_params)):

        res = minimize(fun=acquisition_func,
                       x0=starting_point.reshape(1, -1),
                       bounds=bounds,
                       method='L-BFGS-B',
                       args=(gaussian_process, evaluated_loss, greater_is_better, n_params))

        if res.fun < best_acquisition_value:
            best_acquisition_value = res.fun
            best_x = res.x

    return best_x


def bayesian_optimisation(n_iters, sample_loss, bounds, DAG_arn, x0=None, n_pre_samples=5,
                          gp_params=None, random_search=False, alpha=1e-5, epsilon=1e-7):
    """ bayesian_optimisation
    Uses Gaussian Processes to optimise the loss function `sample_loss`.
    Arguments:
    ----------
        n_iters: integer.
            Number of iterations to run the search algorithm.
        sample_loss: function.
            Function to be optimised.
        bounds: array-like, shape = [n_params, 2].
            Lower and upper bounds on the parameters of the function `sample_loss`.
        x0: array-like, shape = [n_pre_samples, n_params].
            Array of initial points to sample the loss function for. If None, randomly
            samples from the loss function.
        n_pre_samples: integer.
            If x0 is None, samples `n_pre_samples` initial points from the loss function.
        gp_params: dictionary.
            Dictionary of parameters to pass on to the underlying Gaussian Process.
        random_search: integer.
            Flag that indicates whether to perform random search or L-BFGS-B optimisation
            over the acquisition function.
        alpha: double.
            Variance of the error term of the GP.
        epsilon: double.
            Precision tolerance for floats.
    """

    x_list = []
    y_list = []

    n_params = bounds.shape[0]

    if x0 is None:
        for params in np.random.uniform(bounds[:, 0], bounds[:, 1], (n_pre_samples, bounds.shape[0])):
            x_list.append(params)
            y_list.append(sample_loss(params, DAG_arn))
    else:
        for params in x0:
            x_list.append(params)
            y_list.append(sample_loss(params, DAG_arn))

    xp = np.array(x_list)
    yp = np.array(y_list)

    # Create the GP
    if gp_params is not None:
        model = gp.GaussianProcessRegressor(**gp_params)
    else:
        kernel = gp.kernels.Matern()
        model = gp.GaussianProcessRegressor(kernel=kernel,
                                            alpha=alpha,
                                            n_restarts_optimizer=10,
                                            normalize_y=True)
    
    for n in range(n_iters):

        model.fit(xp, yp)

        # Sample next hyperparameter
        if random_search:
            x_random = np.random.uniform(bounds[:, 0], bounds[:, 1], size=(random_search, n_params))
            ei = -1 * expected_improvement(x_random, model, yp, greater_is_better=True, n_params=n_params)
            next_sample = x_random[np.argmax(ei), :]
        else:
            next_sample = sample_next_hyperparameter(expected_improvement, model, yp, greater_is_better=True, bounds=bounds, n_restarts=1)

        # Duplicates will break the GP. In case of a duplicate, we will randomly sample a next query point.
        if np.any(np.abs(next_sample - xp) <= epsilon):
            next_sample = np.random.uniform(bounds[:, 0], bounds[:, 1], bounds.shape[0])

        # Sample loss for new set of parameters
        cv_score = sample_loss(next_sample, DAG_arn)

        # Update lists
        x_list.append(next_sample)
        y_list.append(cv_score)

        # Update xp and yp
        xp = np.array(x_list)
        yp = np.array(y_list)

    return xp, yp

def main():
    args = sys.argv[1:]
    if(len(args) == 0):
        print("Please enter the DAG's arn as the first argument")
        return

    if(len(args) == 1):
        print("Please enter the Latency target as the second argument")
        return

    DAG_arn = args[0]     
    print(DAG_arn)
    bounds = np.array([[192,10240], [512,10240], [192,10240]])    # video
    x,y = bayesian_optimisation(2, minimized_function, bounds, DAG_arn)    
    target = int(args[1])
    min_diff = target * 1000
    for i in range(len(x)):
        diff = abs(int(y[i]) - int(target))
        if diff < min_diff:
           min_diff = diff
           best_index = i
        
    print("Best VM sizes configs:")
    print(x[best_index])

main()	
