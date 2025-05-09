Intellexia is a simple python application to run Long Language Models inference on the NPU for Intel Core Ultra processors as Meteor Lake and Lunar Lake with Openvino. 
Enjoy the low power consumption and privacy to use your own language model locally without restrictions. 

Tested only on Ubuntu 24.04 but should work on other distributions and also on Windows

- Installation:

GPU Support:
sudo apt update
sudo apt install -y gpg-agent wget
wget -qO - https://repositories.intel.com/gpu/intel-graphics.key | sudo gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg
echo "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/gpu/ubuntu noble client" | sudo tee /etc/apt/sources.list.d/intel-gpu-noble.list
sudo apt install -y \
 intel-opencl-icd intel-level-zero-gpu level-zero \
 intel-media-va-driver-non-free libmfx1 libmfxgen1 libvpl2 \
 libegl-mesa0 libegl1-mesa-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri \
 libglapi-mesa libgles2-mesa-dev libglx-mesa0 libigdgmm12 libxatracker2 mesa-va-drivers \
 mesa-vdpau-drivers mesa-vulkan-drivers va-driver-all vainfo hwinfo clinfo
sudo reboot

NPU Support:
sudo apt install libtbb12
wget https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-driver-compiler-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb
wget https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-fw-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb
wget https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-level-zero-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb
wget https://github.com/oneapi-src/level-zero/releases/download/v1.18.5/level-zero_1.18.5+u24.04_amd64.deb
sudo dpkg -i *.deb
sudo bash -c "echo 'SUBSYSTEM==\"accel\", KERNEL==\"accel*\", GROUP=\"render\", MODE=\"0660\"' > /etc/udev/rules.d/10-intel-vpu.rules"
sudo usermod -a -G render $USER
sudo reboot

- Clone the repository:
git clone https://github.com/JoseMariaZ/Intellexia.git

- Install Dependencies:
pip install nncf==2.12 onnx==1.16.1 optimum-intel==1.19.0
pip install --pre openvino openvino-tokenizers openvino-genai --extra-index-url https://storage.openvinotoolkit.org/simple/wheels/nightly

- Download and install the Models:
cd Models
optimum-cli export openvino -m meta-llama/Llama-3.1-8B-Instruct --weight-format int4 --sym --ratio 1.0 --group-size -1 Llama-3.1-8B-Instruct
optimum-cli export openvino --model dreamlike-art/dreamlike-anime-1.0 --task stable-diffusion --weight-format fp16 dreamlike_anime_1_0_ov/FP16

Run:
python3 Intellexia-Free.py

By default Llama-3.1-8B-Instruct with function calling will run on the NPU and dreamlike-anime-1.0 will use on GPU. 
You can modify the settings on the config.json

4: References
https://github.com/openvinotoolkit/openvino/blob/master/docs/articles_en/learn-openvino/llm_inference_guide/genai-guide-npu.rst

For NPU monitoring on Linux:
https://github.com/DMontgomery40/intel-npu-top