<template>
  <div>
    <el-card>
      <template #header>室内定位地图</template>
      <el-alert type="info" :closable="false" style="margin-bottom: 16px;">
        此功能需要配合定位信标硬件设备使用。当前为演示模式。
      </el-alert>
      <div class="map-container">
        <div class="floor-plan">
          <div v-for="pos in positions" :key="pos.id" class="position-dot"
            :style="{ left: pos.x + '%', top: pos.y + '%' }"
            :class="{ restricted: pos.is_in_restricted_zone }">
            <el-tooltip :content="`${pos.resident_name} - ${pos.floor}F`">
              <div class="dot"></div>
            </el-tooltip>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getPositions } from '@/api/smartDetection'

const positions = ref([])

onMounted(async () => {
  try {
    const data = await getPositions({ page_size: 50 })
    positions.value = data.results || data
  } catch { /* empty */ }
})
</script>

<style lang="scss" scoped>
.map-container { position: relative; height: 500px; background: #f5f7fa; border-radius: 8px; overflow: hidden; }
.floor-plan { position: relative; width: 100%; height: 100%; }
.position-dot {
  position: absolute; transform: translate(-50%, -50%);
  .dot {
    width: 16px; height: 16px; border-radius: 50%; background: #409EFF;
    animation: pulse 2s infinite;
  }
  &.restricted .dot { background: #F56C6C; }
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(64, 158, 255, 0); }
  100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0); }
}
</style>
