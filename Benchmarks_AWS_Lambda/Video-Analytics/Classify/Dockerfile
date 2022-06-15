FROM public.ecr.aws/lambda/python:3.7

RUN pip3 install tensorflow==2.4.0 keras==2.4.3 numpy==1.19.3 pillow==7.0.0 scipy==1.4.1 h5py==2.10.0 matplotlib==3.3.2 opencv-python keras-resnet==0.2.0 --target "${LAMBDA_TASK_ROOT}"

RUN pip3 install imageai --upgrade --target "${LAMBDA_TASK_ROOT}"

RUN mkdir -p ~/models
RUN mkdir -p ~/images
RUN mkdir -p ~/tmp_out

COPY app_s3_step.py ${LAMBDA_TASK_ROOT}
CMD ["app_s3_step.handler"]      

COPY models/yolo-tiny.h5 ~/models/yolo-tiny.h5
COPY input.jpg ~/images/input.jpg
COPY input_fast.jpg ~/images/input_fast.jpg
COPY input_slow.jpg ~/images/input_slow.jpg
