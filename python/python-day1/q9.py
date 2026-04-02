from dotenv import dotenv_values
def load_env(file_path):
    env_vars={}
    with open(r"C:\practice\day2\.env",'r')as file:
        for line in file:
            line=line.strip()

            if not line or line.startswith('#'):
                continue
            key,value=line.split('=',1)
            env_vars[key.strip()]=value.strip()

    return env_vars
env=load_env(".env")
print(env)



