<template>
  <div class="vital-monitor">
    <el-card class="filter-card">
      <el-form :inline="true">
        <el-form-item label="选择老人">
          <el-select v-model="selectedResident" filterable placeholder="请选择" @change="loadVitals">
            <el-option v-for="r in residents" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="16" v-if="latestVitals" class="vital-cards">
      <el-col :span="4" v-for="item in vitalItems" :key="item.key">
        <el-card :class="['vital-card', isAbnormal(item.key) ? 'abnormal' : '']" shadow="hover">
          <div class="vital-value">{{ latestVitals[item.key] ?? '--' }}</div>
          <div class="vital-label">{{ item.label }}</div>
          <div class="vital-unit">{{ item.unit }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card v-if="selectedResident" style="margin-top: 16px;">
      <template #header>体征趋势图</template>
      <div ref="trendChartRef" style="height: 400px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getResidents } from '@/api/residents'
import { getLatestVitals, getVitalTrends } from '@/api/smartDetection'

const residents = ref([])
const selectedResident = ref('')
const latestVitals = ref(null)
const trends = ref([])
const trendChartRef = ref()

const vitalItems = [
  { key: 'heart_rate', label: '心率', unit: 'bpm' },
  { key: 'systolic_bp', label: '收缩压', unit: 'mmHg' },
  { key: 'diastolic_bp', label: '舒张压', unit: 'mmHg' },
  { key: 'blood_oxygen', label: '血氧', unit: '%' },
  { key: 'temperature', label: '体温', unit: '°C' },
  { key: 'respiratory_rate', label: '呼吸率', unit: '次/分' },
]

function isAbnormal(key) {
  return latestVitals.value?.abnormal_items?.includes(key)
}

async function loadVitals() {
  if (!selectedResident.value) return
  try {
    latestVitals.value = await getLatestVitals(selectedResident.value)
    trends.value = await getVitalTrends(selectedResident.value, { days: 7 })
    await nextTick()
    renderChart()
  } catch { /* empty */ }
}

function renderChart() {
  if (!trendChartRef.value || !trends.value.length) return
  const chart = echarts.init(trendChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['心率', '血氧', '体温'] },
    xAxis: { type: 'category', data: trends.value.map((t) => t.measured_at?.slice(5, 16)) },
    yAxis: [
      { type: 'value', name: '心率/血氧' },
      { type: 'value', name: '体温', min: 35, max: 40 },
    ],
    series: [
      { name: '心率', type: 'line', data: trends.value.map((t) => t.heart_rate), smooth: true },
      { name: '血氧', type: 'line', data: trends.value.map((t) => t.blood_oxygen), smooth: true },
      { name: '体温', type: 'line', yAxisIndex: 1, data: trends.value.map((t) => t.temperature), smooth: true },
    ],
  })
}

onMounted(async () => {
  const data = await getResidents({ status: 'active', page_size: 100 })
  residents.value = data.results || data
})
</script>

<style lang="scss" scoped>
.vital-cards { margin-top: 16px; }
.vital-card {
  text-align: center;
  padding: 16px;
  &.abnormal {
    border-color: #F56C6C;
    background: #fef0f0;
  }
}
.vital-value { font-size: 28px; font-weight: bold; color: #303133; }
.vital-label { font-size: 14px; color: #909399; margin-top: 4px; }
.vital-unit { font-size: 12px; color: #c0c4cc; }
</style>
