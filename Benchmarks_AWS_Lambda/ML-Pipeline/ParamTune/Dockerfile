FROM public.ecr.aws/lambda/python:3.7

RUN pip3 install tensorflow==2.4.0 keras==2.4.3 numpy==1.19.3 pillow==7.0.0 scipy==1.4.1 h5py==2.10.0 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 lightgbm 


COPY params.py ./
COPY lambda_function.py   ./
CMD ["lambda_function.handler"]      

