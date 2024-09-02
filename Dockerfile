FROM ubuntu:latest

WORKDIR /usr/app/src

#download and install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        apt-utils \
        #build essential 
        locales \
        python3-pip \
        python3-yaml \
        rsyslog systemd systemd-cron sudo \
    && apt-get clean

RUN pip3 install --upgrade pip
 
RUN pip3 install streamlit \ 
    crewai \
    streamlit  \
    openai \     
    unstructured \
    tools \
    tenacity==8.3.0 \
    streamlit-shadcn-ui \
    langchain \
    langchain_groq \
    streamlit-extras \
    cohere \
    borb \
    fpdf 



COPY / ./

# Tell the Image what to do when it starts the container
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.enableCORS=false"]
