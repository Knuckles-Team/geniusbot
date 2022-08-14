#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
import torch
import psutil
import os
import time


class ChatBot():
    def __init__(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        self.model = None
        self.tokenizer = None
        self.generator = None
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.memory_required = 20 #GB
        self.bytes = 1073741824
        self.loaded = False

    def check_hardware(self):
        self.total_memory = psutil.virtual_memory()[0]
        self.used_memory = psutil.virtual_memory()[3]
        self.free_memory = psutil.virtual_memory()[1]
        self.used_percent = psutil.virtual_memory()[2]
        print(f"Required RAM: {self.memory_required} GB\n"
              f"Used RAM: {round(float(self.used_memory/self.bytes), 2)} GB\n"
              f"Free RAM: {round(float((self.free_memory)/self.bytes), 2)} GB\n"
              f"Total RAM: {round(float(self.total_memory/self.bytes), 2)} GB\n"
              f"RAM Utilization Percentage: {round(self.used_percent, 2)}%")

    def save_model(self):
        if os.path.isfile("geniusbot_gptj.pt"):
            print("Model already downloaded")
        else:
            print("Downloading model")
            # load fp 16 model
            model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16, low_cpu_mem_usage=True)
            # save model with torch.save
            print("Saving model")
            torch.save(model, "geniusbot_gptj.pt")
            print("Model Saved")

    def load_model(self):
        if self.free_memory >= (self.memory_required*self.bytes):
            print("Loading Model")
            # # load model
            # self.model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16, low_cpu_mem_usage=True)
            # self.model.load_state_dict(torch.load("geniusbot_gptj.pt"))
            # self.model.device(self.device)
            # # load tokenizer
            # self.tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")
            # # create pipeline
            # self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=0)
            # print("Model Loaded")
            # # run prediction
            # self.generator("My Name is GeniusBot")
            # self.loaded = True


            # https://www.pragnakalp.com/gpt-j-6b-parameters-model-huggingface/
            self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-j-6B",
                                                              revision="float16",
                                                              torch_dtype=torch.float16,
                                                              low_cpu_mem_usage=True)

            print("Model Loaded..!")

            start_time = time.time()

            input_text = "My Name is GeniusBot"
            inputs = self.tokenizer(input_text, return_tensors="pt")
            input_ids = inputs["input_ids"]

            output = self.model.generate(
                input_ids,
                attention_mask=inputs["attention_mask"],
                do_sample=True,
                max_length=150,
                temperature=0.8,
                use_cache=True,
                top_p=0.9
            )

            end_time = time.time() - start_time
            print("Total Taken => ", end_time)
            print(self.tokenizer.decode(output[0]))
            self.loaded = True
        else:
            print(f"Device doesn't have at least {self.memory_required} GB of RAM. "
                  f"Available RAM: {round(float(self.free_memory / self.bytes), 2)}")
            self.loaded = False

    def chat(self, text):
        generated_response = self.generator(text)
        return generated_response

    def get_loaded(self):
        return self.loaded


if __name__ == "__main__":
    geniusbot_chat = ChatBot()
    geniusbot_chat.check_hardware()
    geniusbot_chat.save_model()
    geniusbot_chat.load_model()
