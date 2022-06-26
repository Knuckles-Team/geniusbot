from transformers import AutoTokenizer, GPTJForCausalLM, pipeline, AutoModelForCausalLM
import torch

def save_model():
    # load fp 16 model
    #model = GPTJForCausalLM.from_pretrained("EleutherAI/gpt-j-6B", revision="float16", torch_dtype=torch.float16)
    model = AutoModelForCausalLM.from_pretrained("ykilcher/gpt-4chan",  revision="float16", torch_dtype=torch.float16)
    # save model with torch.save
    #torch.save(model, "gpt4chan.pt")
    torch.save(model, "gptj.pt")


def load_model():
    # load model
    model = torch.load("gptj.pt")
    # load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")

    # create pipeline
    gen = pipeline("text-generation",model=model,tokenizer=tokenizer,device=0)

    # run prediction
    gen("My Name is philipp")
    #[{'generated_text': 'My Name is philipp k. and I live just outside of Detroit....


save_model()
load_model()