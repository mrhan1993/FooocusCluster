import pycuda.driver as cuda
import pycuda.autoinit

from tools.logger import common_logger


class GlobalMemory:
    """
    用于存储参数中的图像映射
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GlobalMemory, cls).__new__(cls, *args, **kwargs)
            cls._instance._data = {}
        return cls._instance

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key, None)

    def delete(self, key):
        if key in self._data:
            del self._data[key]

    def clear(self):
        self._data.clear()

    def __str__(self):
        return str(self._data)


def get_cuda_flops() -> tuple:
    """
    获取当前设备支持的 TFlops 数值。
    :return: TFlops 以及显存大小
    """
    cores_per_multiprocessor = {
        1: 8,   # Tesla architecture (sm_1X)
        2: 32,  # Fermi architecture (sm_2X)
        3: 192, # Kepler architecture (sm_3X)
        5: 128, # Maxwell architecture (sm_5X)
        6: 64,  # Pascal architecture (sm_6X)
        7: 64,  # Volta and Turing architecture (sm_7X)
        8: 128, # Ampere architecture (sm_8X)
    }
    try:
        device = cuda.Device(0)  # 选择第一个 GPU 设备
        attrs = device.get_attributes()
        sm_version = attrs[cuda.device_attribute.COMPUTE_CAPABILITY_MAJOR]
        cores_per_sm = cores_per_multiprocessor.get(sm_version, 64)  # 默认值为64
        num_sms = attrs[cuda.device_attribute.MULTIPROCESSOR_COUNT]
        core_clock = int(attrs[cuda.device_attribute.CLOCK_RATE] / 1000)

        total_memory = round(device.total_memory() / (1024**3))
        cuda_core_nums = num_sms * cores_per_sm
        # TFlops = (CUDA 核心数 × 核心频率 × 2) / 10^12
        flops = (cuda_core_nums * core_clock * 2) / 10**6
        return int(flops) / 10, total_memory
    except Exception as e:
        common_logger.error(f"[Common] 获取 CUDA 显存信息失败，错误信息为：{e}")
        return 0, 0