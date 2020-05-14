import os, sys, h5py
from tfrecord_data import input_fn
import tensorflow as tf
import json
# from keras.optimizers import RMSprop

from vae_conv import conv_variational_autoencoder
# sys.path.append('/home/hm0/Research/molecules/molecules_git/build/lib')
# from molecules.ml.unsupervised import VAE
# from molecules.ml.unsupervised import EncoderConvolution2D
# from molecules.ml.unsupervised import DecoderConvolution2D
# from molecules.ml.unsupervised.callbacks import EmbeddingCallback 

# def CVAE(input_shape, hyper_dim=3): 
#     optimizer = RMSprop(lr=0.001, rho=0.9, epsilon=1e-08, decay=0.0)

#     encoder = EncoderConvolution2D(input_shape=input_shape)

#     encoder._get_final_conv_params()
#     num_conv_params = encoder.total_conv_params
#     encode_conv_shape = encoder.final_conv_shape

#     decoder = DecoderConvolution2D(output_shape=input_shape,
#                                    enc_conv_params=num_conv_params,
#                                    enc_conv_shape=encode_conv_shape)

#     cvae = VAE(input_shape=input_shape,
#                latent_dim=hyper_dim,
#                encoder=encoder,
#                decoder=decoder,
#                optimizer=optimizer) 
#     return cvae 

def CVAE(input_shape, latent_dim=3): 
    image_size = input_shape[:-1]
    channels = input_shape[-1]
    conv_layers = 4
    feature_maps = [64,64,64,64]
    filter_shapes = [(3,3),(3,3),(3,3),(3,3)]
    strides = [(1,1),(2,2),(1,1),(1,1)]
    dense_layers = 1
    dense_neurons = [128]
    dense_dropouts = [0]

    feature_maps = feature_maps[0:conv_layers];
    filter_shapes = filter_shapes[0:conv_layers];
    strides = strides[0:conv_layers];
    autoencoder = conv_variational_autoencoder(image_size,channels,conv_layers,feature_maps,
               filter_shapes,strides,dense_layers,dense_neurons,dense_dropouts,latent_dim); 
    autoencoder.model.summary()
    return autoencoder


def run_cvae_tfrecords(gpu_id, cm_file, hyper_dim=3, epochs=100, batch_size=1000): 
    tfrecords_fname = "../tfrecords-metadata.json"
    if os.path.isfile(tfrecords_fname):
        with open(tfrecords_fname, 'r') as f:
            metadata = json.load(f)
            shape0 = metadata['shape0']
            shape1 = metadata['shape1']
            shape2 = metadata['shape2']
            params = {}
            params['shape0'] = shape0
            params['shape1'] = shape1
            params['shape2'] = shape2

    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    #os.environ["CUDA_VISIBLE_DEVICES"]=str(gpu_id) 
    #train_dataset = input_fn(batch_size, filename=cm_file, is_training=True, params=None) 
    #val_dataset = input_fn(batch_size, filename=cm_file, is_training=False, params=None)
   # print(type(train_dataset))    
   # cvae = CVAE(train_dataset.shape[1:], hyper_dim) 
    
    cvae = CVAE([shape0, shape1, shape2], hyper_dim)
    cvae.set_tfrecords(cm_file)
    
#     callback = EmbeddingCallback(cm_data_train, cvae)
    cvae.train([], batch_size = batch_size, epochs=epochs) 
    
    return cvae 

def run_cvae(gpu_id, cm_file, hyper_dim=3, epochs=100): 
    # read contact map from h5 file 
    cm_h5 = h5py.File(cm_file, 'r', libver='latest', swmr=True)
    cm_data_input = cm_h5[u'contact_maps'] 

    # splitting data into train and validation
    train_val_split = int(0.8 * len(cm_data_input))
    #cm_data_train, cm_data_val = cm_data_input[:train_val_split], cm_data_input[train_val_split:] 
    cm_data_train = cm_data_input[:train_val_split]
    input_shape = cm_data_input.shape
    del(cm_data_input)
    cm_h5.close()
    
    os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    #os.environ["CUDA_VISIBLE_DEVICES"]=str(gpu_id) 
    
    cvae = CVAE(input_shape[1:], hyper_dim) 
    
#     callback = EmbeddingCallback(cm_data_train, cvae)
    cvae.train(cm_data_train, batch_size = 64, epochs=epochs) 
    
    return cvae 
