#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
from torch.quantization.qconfig import float_qparams_weight_only_qconfig
import torch

def save_model():
    print("Downloading model")
    # load fp 16 model
    model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16, low_cpu_mem_usage=True)
    # save model with torch.save
    print("Saving model")
    torch.save(model, "geniusbot_gptj.pt")
    print("Model Saved")


def load_model():
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
    gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)

    # run prediction
    gen("My Name is GeniusBot")
    #[{'generated_text': 'My Name is philipp k. and I live just outside of Detroit....
    print("Model Loaded")


#save_model()
load_model()