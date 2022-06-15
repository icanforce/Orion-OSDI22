using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DAG_Modeler
{
    public struct distribution_params
    {
        public double mu;
        public double sigma;

    }
    public class Stage
    {
        string name = "";
        Dictionary<long, List<double>> resource_to_latency_list = new Dictionary<long, List<double>>();
        Dictionary<long, List<List<double>>> resource_to_latency_group_list = new Dictionary<long, List<List<double>>>();

        Dictionary<long, double> resource_to_mu = new Dictionary<long, double>();
        Dictionary<long, double> resource_to_sigma = new Dictionary<long, double>();

        Dictionary<long, PDF> stage_PDF = new Dictionary<long, PDF>();
        Dictionary<long, CDF> stage_CDF = new Dictionary<long, CDF>();

        Dictionary<long, CDF> stage_joint_CDF = new Dictionary<long, CDF>();

        public string Name { get => name; set => name = value; }
        public Dictionary<long, List<double>> Resource_to_latency_list { get => resource_to_latency_list; set => resource_to_latency_list = value; }
        public Dictionary<long, double> Resource_to_mu { get => resource_to_mu; set => resource_to_mu = value; }
        public Dictionary<long, double> Resource_to_sigma { get => resource_to_sigma; set => resource_to_sigma = value; }
        public Dictionary<long, PDF> Stage_PDF { get => stage_PDF; set => stage_PDF = value; }
        public Dictionary<long, CDF> Stage_CDF { get => stage_CDF; set => stage_CDF = value; }
        public Dictionary<long, CDF> Stage_Conditional_CDF { get => stage_joint_CDF; set => stage_joint_CDF = value; }
        public Dictionary<long, List<List<double>>> Resource_to_latency_group_list { get => resource_to_latency_group_list; set => resource_to_latency_group_list = value; }

        public void fill_PDF_CDF()
        {

            for (int i = 0; i < resource_to_latency_list.Count; i++)
            {
                long key = resource_to_latency_list.ElementAt(i).Key;
                stage_PDF.Add(key, new PDF(resource_to_latency_list.ElementAt(i).Value));
                stage_CDF.Add(key, CDF_PDF_Manager.get_cdf(stage_PDF[key]));
            }

        }

        public void extractMeanStd()
        {
            for (int i = 0; i < resource_to_latency_list.Count; i++)
            {
                resource_to_latency_list[resource_to_latency_list.ElementAt(i).Key] = resource_to_latency_list.ElementAt(i).Value.OrderByDescending(x => x).ToList();
                // delete first execution to remove the impact of cold starts
                //if (resource_to_latency_list.ElementAt(i).Value.Count > 0)
                //    resource_to_latency_list.ElementAt(i).Value.RemoveAt(0);

                double avg = resource_to_latency_list.ElementAt(i).Value.Average();
                resource_to_mu.Add(resource_to_latency_list.ElementAt(i).Key, avg);

                double sum = resource_to_latency_list.ElementAt(i).Value.Sum(d => Math.Pow(d - avg, 2));
                double standardDeviation = Math.Sqrt((sum) / (resource_to_latency_list.ElementAt(i).Value.Count()));

                resource_to_sigma.Add(resource_to_latency_list.ElementAt(i).Key, standardDeviation);
            }

        }

        public distribution_params estimate_params(long resource)
        {
            distribution_params returned_params = new distribution_params();
            if (Resource_to_mu.ContainsKey(resource) && Resource_to_sigma.ContainsKey(resource)) // already profiled this memory size
            {
                returned_params.mu = Resource_to_mu[resource];
                returned_params.sigma = Resource_to_sigma[resource];
                return returned_params;
            }
            else
            {
                for (int i = 1; i < resource_to_mu.Count; i++)
                {
                    double R1 = resource_to_mu.ElementAt(i - 1).Key;
                    double R2 = resource_to_mu.ElementAt(i).Key;
                    double mu1 = resource_to_mu.ElementAt(i - 1).Value;
                    double mu2 = resource_to_mu.ElementAt(i).Value;
                    double std1 = resource_to_sigma.ElementAt(i - 1).Value;
                    double std2 = resource_to_sigma.ElementAt(i).Value;

                    if (resource > R1 && resource < R2) // found in range 
                    {
                        returned_params.mu = mu1 + ((resource - R1) / (R2 - R1) * (mu2 - mu1));
                        returned_params.sigma = std1 + ((resource - R1) / (R2 - R1) * (std2 - std1));
                        return returned_params;
                    }
                }
            }
            return new distribution_params();
        }
    }
}
