# Setup Ollama

## Nvidia GPU

### Install the NVIDIA Container Toolkit.

Install with Apt:

1. Configure the repository
```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
```

2. Install the NVIDIA Container Toolkit packages
```bash
sudo apt-get install -y nvidia-container-toolkit
```

## Configure Docker to use Nvidia driver

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart dockers
```

## Start the container

```bash
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

## Troubleshuting

1. W/O the permision during run docker
  - Add User with Sudo: `sudo usermod -aG docker $USER` and restart

## Reference
- [Ollama Doc](https://docs.ollama.com/docker#start-the-container)
