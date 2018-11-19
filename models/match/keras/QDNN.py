# -*- coding: utf-8 -*-

from models.match.keras.SiameseNetwork import SiameseNetwork
from models.representation.keras.QDNN import QDNN as representation_model

class QDNN(SiameseNetwork):
    
    def initialize(self):
        super(SiameseNetwork, self).initialize()
        self.representation_model = representation_model(self.opt)
    def __init__(self,opt):
        super(SiameseNetwork, self).__init__(opt) 
