#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
from torch.quantization.qconfig import float_qparams_weight_only_qconfig
import torch
import psutil

class ChatBot():
    def __init__(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]

    def check_hardware(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        print(f"Used RAM: {round(float(self.used_memory/1073741824), 2)} GB\n"
              f"Free RAM: {round(float((self.free_memory)/1073741824), 2)} GB\n"
              f"Total RAM: {round(float(self.total_memory/1073741824), 2)} GB\n"
              f"RAM Utilization Percentage: {round(self.used_percent, 2)}%")

    def save_model(self):
        print("Downloading model")
        # load fp 16 model
        model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16, low_cpu_mem_usage=True)
        # save model with torch.save
        print("Saving model")
        torch.save(model, "geniusbot_gptj.pt")
        print("Model Saved")

    def load_model(self):
        if self.free_memory >= 15032385536:
            print("Loading Model")
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            #torch.device('cpu')
            # load model
            #model = torch.load("geniusbot_gptj.pt")#.to("cuda",  torch_dtype=torch.float16)
            #model = torch.load("geniusbot_gptj.pt", map_location=torch.device('cpu'))
            model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16, low_cpu_mem_usage=True)
            model.load_state_dict(torch.load("geniusbot_gptj.pt"))
            model.device(device)
            # model = Model()
            # model.load_state_dict(torch.load("geniusbot_gptj.pt", map_location=torch.device('cpu')))
            # torch.load('tensors.pt', map_location=lambda storage, loc: storage.cuda(1))
            # load tokenizer
            tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")
            #input_ids = tokenizer(context, return_tensors="pt").input_ids.to("cuda")
            # create pipeline
            gen = pipeline("text-generation", model=model, tokenizer=tokenizer)

            # run prediction
            gen("My Name is GeniusBot")
            #[{'generated_text': 'My Name is philipp k. and I live just outside of Detroit....
            print("Model Loaded")
        else:
            print(f"Device doesn't have at least 14 GB of RAM. Available RAM: {round(float((self.free_memory)/1073741824), 2)}")

if __name__ == "__main__":
    geniusbot_chat = ChatBot()
    # geniusbot_chat.save_model()
    geniusbot_chat.check_hardware()
    geniusbot_chat.load_model()

    #geniusbot(sys.argv[1:])
