from langchain_core.runnables import RunnablePassthrough, RunnableLambda

print(RunnablePassthrough.assign(B=lambda a: a).invoke({"A": 1}))