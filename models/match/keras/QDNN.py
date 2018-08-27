
# -*- coding: utf-8 -*-
from .BasicModel import BasicModel
from keras.layers import Embedding, GlobalMaxPooling1D,Dense, Masking, Flatten,Dropout, Activation,concatenate,Reshape, Permute,Lambda, Subtract
from keras.models import Model, Input, model_from_json, load_model, Sequential
from keras.constraints import unit_norm
from complexnn import *
import math
import numpy as np

from keras import regularizers
import keras.backend as K
from models.representation.QDNN import QDNN as rep_model

class QDNN(BasicModel):
    
    def initialize(self):
        self.question = Input(shape=(self.opt.max_sequence_length,), dtype='float32')
        self.answer = Input(shape=(self.opt.max_sequence_length,), dtype='float32')
        self.neg_answer = Input(shape=(self.opt.max_sequence_length,), dtype='float32')
        self.phase_embedding=phase_embedding_layer(self.opt.max_sequence_length, self.opt.lookup_table.shape[0], self.opt.lookup_table.shape[1], trainable = self.opt.embedding_trainable,l2_reg=self.opt.phase_l2)
        self.amplitude_embedding = amplitude_embedding_layer(np.transpose(self.opt.lookup_table), self.opt.max_sequence_length, trainable = self.opt.embedding_trainable, random_init = self.opt.random_init,l2_reg=self.opt.amplitude_l2)
        self.weight_embedding = Embedding(self.opt.lookup_table.shape[0], 1, trainable = True)
        self.dense = Dense(self.opt.nb_classes, activation=self.opt.activation, kernel_regularizer= regularizers.l2(self.opt.dense_l2))  # activation="sigmoid",
        self.dropout_embedding = Dropout(self.opt.dropout_rate_embedding)
        self.dropout_probs = Dropout(self.opt.dropout_rate_probs)
        self.projection = ComplexMeasurement(units = self.opt.measurement_size)
        
        self.distance = Lambda(cosine_similarity)
        
    def __init__(self,opt):
        super(QDNN, self).__init__(opt) 
        
    def build(self):
        rep_m = rep_model(self.opt)
        if self.opt.match_type == 'pointwise':
            rep = []
            for doc in [self.question, self.answer]:
                # Take the real part of the output
                rep.append(rep_m.get_representation(doc))

            output = self.distance(rep)
            
            model = Model([self.question, self.answer], output)
        elif self.opt.match_type == 'pairwise':
            rep = []
            for doc in [self.question, self.answer, self.neg_answer]:
                rep.append(rep_m.get_representation(doc))
            output = rep
            model = Model([self.question, self.answer, self.neg_answer], output)           
        else:
            raise ValueError('wrong input of matching type. Please input pairwise or pointwise.')
        return model
        


if __name__ == "__main__":
    from models.BasicModel import BasicModel
    from params import Params
    import numpy as np
    import dataset
    import units
    opt = Params()
    config_file = 'config/local.ini'    # define dataset in the config
    opt.parse_config(config_file)
    reader = dataset.setup(opt)
    opt = dataset.process_embedding(reader,opt)
    
    (train_x, train_y),(test_x, test_y),(val_x, val_y) = reader.get_processed_data()
    train_y = np.random.randint(2,size = len(train_y))
    self = BasicModel(opt)
#    model.compile(loss = opt.loss,
#            optimizer = units.getOptimizer(name=opt.optimizer,lr=opt.lr),
#            metrics=['accuracy'])
#    print(model.predict(x = [train_x,train_x]))
#    

