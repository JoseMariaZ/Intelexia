<p class="has-line-data" data-line-start="0" data-line-end="2">Intellexia is a simple python application to run Long Language Models inference on the NPU for Intel Core Ultra processors as Meteor Lake and Lunar Lake with Openvino.<br>
Enjoy the low power consumption and privacy to use your own language model locally without restrictions.</p>
<p class="has-line-data" data-line-start="3" data-line-end="4">Tested only on Ubuntu 24.04 but should work on other distributions and also on Windows</p>
<ul>
<li class="has-line-data" data-line-start="5" data-line-end="7">Installation:</li>
</ul>
<p class="has-line-data" data-line-start="7" data-line-end="19">GPU Support:<br>
sudo apt update<br>
sudo apt install -y gpg-agent wget<br>
wget -qO - <a href="https://repositories.intel.com/gpu/intel-graphics.key">https://repositories.intel.com/gpu/intel-graphics.key</a> | sudo gpg --yes --dearmor --output /usr/share/keyrings/intel-graphics.gpg<br>
echo “deb [arch=amd64,i386 signed-by=/usr/share/keyrings/intel-graphics.gpg] <a href="https://repositories.intel.com/gpu/ubuntu">https://repositories.intel.com/gpu/ubuntu</a> noble client” | sudo tee /etc/apt/sources.list.d/intel-gpu-noble.list<br>
sudo apt install -y <br>
intel-opencl-icd intel-level-zero-gpu level-zero <br>
intel-media-va-driver-non-free libmfx1 libmfxgen1 libvpl2 <br>
libegl-mesa0 libegl1-mesa-dev libgbm1 libgl1-mesa-dev libgl1-mesa-dri <br>
libglapi-mesa libgles2-mesa-dev libglx-mesa0 libigdgmm12 libxatracker2 mesa-va-drivers <br>
mesa-vdpau-drivers mesa-vulkan-drivers va-driver-all vainfo hwinfo clinfo<br>
sudo reboot</p>
<p class="has-line-data" data-line-start="20" data-line-end="30">NPU Support:<br>
sudo apt install libtbb12<br>
wget <a href="https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-driver-compiler-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb">https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-driver-compiler-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb</a><br>
wget <a href="https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-fw-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb">https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-fw-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb</a><br>
wget <a href="https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-level-zero-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb">https://github.com/intel/linux-npu-driver/releases/download/v1.13.0/intel-level-zero-npu_1.13.0.20250131-13074932693_ubuntu24.04_amd64.deb</a><br>
wget <a href="https://github.com/oneapi-src/level-zero/releases/download/v1.18.5/level-zero_1.18.5+u24.04_amd64.deb">https://github.com/oneapi-src/level-zero/releases/download/v1.18.5/level-zero_1.18.5+u24.04_amd64.deb</a><br>
sudo dpkg -i <em>.deb<br>
sudo bash -c &quot;echo 'SUBSYSTEM==“accel”, KERNEL==&quot;accel</em>“, GROUP=“render”, MODE=“0660”’ &gt; /etc/udev/rules.d/10-intel-vpu.rules”<br>
sudo usermod -a -G render $USER<br>
sudo reboot</p>
<ul>
<li class="has-line-data" data-line-start="31" data-line-end="34">
<p class="has-line-data" data-line-start="31" data-line-end="33">Clone the repository:<br>
git clone <a href="https://github.com/JoseMariaZ/Intellexia.git">https://github.com/JoseMariaZ/Intellexia.git</a></p>
</li>
<li class="has-line-data" data-line-start="34" data-line-end="38">
<p class="has-line-data" data-line-start="34" data-line-end="37">Install Dependencies:<br>
pip install nncf<mark>2.12 onnx</mark>1.16.1 optimum-intel==1.19.0<br>
pip install --pre openvino openvino-tokenizers openvino-genai --extra-index-url <a href="https://storage.openvinotoolkit.org/simple/wheels/nightly">https://storage.openvinotoolkit.org/simple/wheels/nightly</a></p>
</li>
<li class="has-line-data" data-line-start="38" data-line-end="43">
<p class="has-line-data" data-line-start="38" data-line-end="42">Download and install the Models:<br>
cd Models<br>
optimum-cli export openvino -m meta-llama/Llama-3.1-8B-Instruct --weight-format int4 --sym --ratio 1.0 --group-size -1 Llama-3.1-8B-Instruct<br>
optimum-cli export openvino --model dreamlike-art/dreamlike-anime-1.0 --task stable-diffusion --weight-format fp16 dreamlike_anime_1_0_ov/FP16</p>
</li>
</ul>
<p class="has-line-data" data-line-start="43" data-line-end="45">Run:<br>
python3 <a href="http://Intellexia-Free.py">Intellexia-Free.py</a></p>
<p class="has-line-data" data-line-start="46" data-line-end="48">By default Llama-3.1-8B-Instruct with function calling will run on the NPU and dreamlike-anime-1.0 will use on GPU.<br>
You can modify the settings on the config.json</p>
<p class="has-line-data" data-line-start="49" data-line-end="51">4: References<br>
<a href="https://github.com/openvinotoolkit/openvino/blob/master/docs/articles_en/learn-openvino/llm_inference_guide/genai-guide-npu.rst">https://github.com/openvinotoolkit/openvino/blob/master/docs/articles_en/learn-openvino/llm_inference_guide/genai-guide-npu.rst</a></p>
<p class="has-line-data" data-line-start="52" data-line-end="54">For NPU monitoring on Linux:<br>
<a href="https://github.com/DMontgomery40/intel-npu-top">https://github.com/DMontgomery40/intel-npu-top</a></p>
