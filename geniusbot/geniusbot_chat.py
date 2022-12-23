#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import transformers
from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
import torch
import psutil
import sys
import os
import getopt
import re


class ChatBot:
    def __init__(self, opt="facebook/opt-125m", model_path=f"{os.curdir}", output_length=20):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        self.model = None
        self.tokenizer = None
        self.device = 'cpu'
        self.torch_dtype = torch.float32
        self.bytes = 1073741824
        self.loaded = False
        self.opt = opt
        self.model_path = model_path
        self.output_length = output_length
        self.low_cpu_usage = True
        self.intelligence_level = "Very Low"

    def set_model_path(self, path):
        self.model_path = path

    def set_model(self, opt):
        self.opt = opt

    def set_output_length(self, output_length):
        self.output_length = output_length

    def set_low_cpu_usage(self, low_cpu_usage):
        self.low_cpu_usage = low_cpu_usage

    def scale_intelligence(self):
        if 5 < round(float((self.free_memory) / self.bytes), 0) < 14:
            self.opt = "facebook/opt-1.3b" #"EleutherAI/gpt-neo-1.3B"
            self.intelligence_level = "Very Low"
        elif 14 < round(float((self.free_memory) / self.bytes), 0) < 22:
            self.opt = "facebook/opt-2.7b"  # "EleutherAI/gpt-neo-2.7B"
            self.intelligence_level = "Low"
        elif 22 < round(float((self.free_memory) / self.bytes), 0) < 45:
            self.opt = "facebook/opt-6.7b" # "EleutherAI/gpt-6j"
            self.intelligence_level = "Medium"
        elif 45 < round(float((self.free_memory) / self.bytes), 0) < 100:
            self.opt = "facebook/opt-13b"
            self.intelligence_level = "High"
        elif 200 < round(float((self.free_memory) / self.bytes), 0):
            self.opt = "facebook/opt-66b"
            self.intelligence_level = "Very High"


    def set_device(self, device):
        if device == 'cpu' or device == 'cuda':
            self.device = device
        if self.device == "cuda":
            self.torch_dtype = torch.float16
        else:
            self.torch_dtype = torch.float32

    def check_hardware(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        print(f"RAM Utilization: {round(self.used_percent, 2)}%\n"
              f"\tUsed  RAM: {round(float(self.used_memory / self.bytes), 2)} GB\n"
              f"\tFree  RAM: {round(float((self.free_memory) / self.bytes), 2)} GB\n"
              f"\tTotal RAM: {round(float(self.total_memory / self.bytes), 2)} GB\n\n")

    def load_model(self):
        print(f"Loading Model: {self.opt}")
        if self.device == "cuda":
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, 
                                                              torch_dtype=self.torch_dtype, 
                                                              local_files_only=True).cuda()
            self.model.to("cude:0")
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_path, torch_dtype=self.torch_dtype, 
                                                              local_files_only=True, 
                                                              low_cpu_mem_usage=self.low_cpu_usage)
        print("Loading Tokenizer")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, 
                                                       local_files_only=True, 
                                                       use_fast=False)
        self.loaded = True
        print("Loading Complete!")

    def save_model(self):
        print(f"Saving model {self.opt} to {self.model_path}")
        self.model = AutoModelForCausalLM.from_pretrained(self.opt,
                                                          torch_dtype=self.torch_dtype,
                                                          low_cpu_mem_usage=self.low_cpu_usage)
        self.tokenizer = AutoTokenizer.from_pretrained(self.opt, use_fast=False)
        self.model.save_pretrained(self.model_path)
        self.tokenizer.save_pretrained(self.model_path)
        print("Save Complete!")
        transformers.utils.move_cache()
        print("Cache Moved Successfully!")

    def chat(self, prompt):
        if self.device == "cuda":
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.cuda()
        else:
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        generated_ids = self.model.generate(input_ids,
                                            do_sample=True, 
                                            max_new_tokens=self.output_length,
                                            top_k=50,
                                            top_p=0.95,
                                            num_return_sequences=9)
        generated_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text

    def get_loaded(self):
        return self.loaded

    def get_intelligence_level(self):
        return self.intelligence_level

    def get_model(self):
        return self.opt


def usage():
    print("geniusbot_chat")


def geniusbot_chat(argv):
    geniusbot_chat = ChatBot()
    run_flag = False
    save_model_flag = False
    prompt = "Geniusbot is the smartest chatbot in existence."

    try:
        opts, args = getopt.getopt(argv, "hrsd:o:p:m:", ["help", "save", "run", 
                                                         "directory=", 
                                                         "output-length=",
                                                         "prompt=", 
                                                         "model="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        elif opt in ('-o', '--output-length'):
            geniusbot_chat.set_output_length(int(arg))
        elif opt in ('-d', '--directory'):
            geniusbot_chat.set_model_path(arg)
        elif opt in ('-p', '--prompt'):
            prompt = str(arg)
        elif opt in ('-s', '--save'):
            save_model_flag = True
        elif opt in ('-r', '--run'):
            run_flag = True
        elif opt in ('-m', '--model'):
            geniusbot_chat.set_model(arg)

    if save_model_flag:
        geniusbot_chat.save_model()

    if run_flag:
        print("RAM Utilization Before Loading Model")
        geniusbot_chat.check_hardware()
        geniusbot_chat.load_model()
        print("RAM Utilization After Loading Model")
        geniusbot_chat.check_hardware()
        print("I'm a friendly artificial intelligence designed to help you with your computer. I can download videos, manage your media library, take full page screenshots of any website, adjust subtitles, and much more")
        print(geniusbot_chat.chat(prompt))


def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    geniusbot_chat(sys.argv[1:])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit(2)
    geniusbot_chat(sys.argv[1:])
    