#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
import torch
import psutil
import os
import re


class ChatBot():
    def __init__(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        self.model = None
        self.tokenizer = None
        self.device = 'cpu'
        #self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.bytes = 1073741824
        self.loaded = False
        self.opt = "facebook/opt-1.3b"
        self.intelligence_level = "Very Low"
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
        self.file_name = f"geniusbot_intelligence_{re.sub('/', '_', self.opt)}.pt"
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
        if self.device == "cuda":
            self.model = AutoModelForCausalLM.from_pretrained(self.opt, torch_dtype=self.torch_dtype).cuda()
            self.model.to("cude:0")
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.opt, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True)
        self.tokenizer = AutoTokenizer.from_pretrained(self.opt, use_fast=False)
        self.loaded = True

    def chat(self, text, output_length=20):
        prompt = text
        if self.device == "cuda":
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.cuda()
        else:
            input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids
        generated_ids = self.model.generate(input_ids, tempurature=0.9, do_sample=False, max_length=output_length)

        generated_text = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text

    def get_loaded(self):
        return self.loaded

    def get_intelligence_level(self):
        return self.intelligence_level

    def get_model(self):
        return self.opt


if __name__ == "__main__":
    geniusbot_chat = ChatBot()
    print("RAM Utilization Before Loading Model")
    geniusbot_chat.check_hardware()
    geniusbot_chat.load_model()
    print("RAM Utilization After Loading Model")
    geniusbot_chat.check_hardware()
    print(geniusbot_chat.chat("I'm a friendly artificial intelligence designed to help you with your computer", output_length=20))
    print(geniusbot_chat.chat("I can download videos, manage your media library, take full page screenshots of any website, adjust subtitles, and much more", output_length=40))
