<template>
  <div class="dashboard">
    <!-- KPI 卡片 -->
    <el-row :gutter="20" class="kpi-row">
      <el-col :span="6" v-for="card in kpiCards" :key="card.title">
        <el-card shadow="hover" class="kpi-card" :body-style="{ padding: '20px' }">
          <div class="kpi-content">
            <div class="kpi-info">
              <div class="kpi-value">{{ card.value }}</div>
              <div class="kpi-title">{{ card.title }}</div>
            </div>
            <el-icon :size="48" :style="{ color: card.color }">
              <component :is="card.icon" />
            </el-icon>
          </div>
          <div class="kpi-footer" v-if="card.sub">{{ card.sub }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card header="近7日呼叫统计">
          <div ref="callChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="设备状态分布">
          <div ref="deviceChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card header="巡更完成率">
          <div class="patrol-stats">
            <el-progress
              type="dashboard"
              :percentage="patrolStats.completion_rate || 0"
              :width="200"
              :color="progressColor"
            />
            <div class="patrol-info">
              <p>今日任务: {{ patrolStats.today_total || 0 }}</p>
              <p>已完成: {{ patrolStats.today_completed || 0 }}</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="床位使用情况">
          <div class="occupancy-info">
            <el-progress
              :percentage="occupancyRate"
              :stroke-width="20"
              :text-inside="true"
              striped
            />
            <p style="margin-top: 12px;">
              已使用 {{ overview.occupancy?.occupied_beds || 0 }} / 总计 {{ overview.occupancy?.total_beds || 0 }}
            </p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getOverview, getCallStats, getPatrolStats } from '@/api/dashboard'
import { getDeviceStatusSummary } from '@/api/campus'

const overview = ref({})
const callStats = ref([])
const patrolStats = ref({})
const deviceStats = ref({})
const callChartRef = ref()
const deviceChartRef = ref()

const kpiCards = computed(() => [
  {
    title: '在住老人',
    value: overview.value.residents?.total || 0,
    icon: 'User',
    color: '#409EFF',
    sub: `今日新增: ${overview.value.residents?.new_today || 0}`,
  },
  {
    title: '活跃呼叫',
    value: overview.value.calls?.active || 0,
    icon: 'Phone',
    color: '#F56C6C',
    sub: `今日总计: ${overview.value.calls?.today_total || 0}`,
  },
  {
    title: '活跃告警',
    value: overview.value.alerts?.active || 0,
    icon: 'Warning',
    color: '#E6A23C',
    sub: `今日总计: ${overview.value.alerts?.today_total || 0}`,
  },
  {
    title: '在线设备',
    value: overview.value.devices?.online || 0,
    icon: 'Monitor',
    color: '#67C23A',
    sub: `故障: ${overview.value.devices?.fault || 0}`,
  },
])

const occupancyRate = computed(() => {
  const { total_beds, occupied_beds } = overview.value.occupancy || {}
  return total_beds ? Math.round((occupied_beds / total_beds) * 100) : 0
})

const progressColor = (percentage) => {
  if (percentage < 50) return '#F56C6C'
  if (percentage < 80) return '#E6A23C'
  return '#67C23A'
}

function renderCallChart() {
  if (!callChartRef.value) return
  const chart = echarts.init(callChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['总呼叫', '紧急呼叫'] },
    xAxis: { type: 'category', data: callStats.value.map((d) => d.date) },
    yAxis: { type: 'value' },
    series: [
      { name: '总呼叫', type: 'bar', data: callStats.value.map((d) => d.total), itemStyle: { color: '#409EFF' } },
      { name: '紧急呼叫', type: 'bar', data: callStats.value.map((d) => d.emergency), itemStyle: { color: '#F56C6C' } },
    ],
  })
}

function renderDeviceChart() {
  if (!deviceChartRef.value || !deviceStats.value.by_status) return
  const chart = echarts.init(deviceChartRef.value)
  const statusLabels = { online: '在线', offline: '离线', fault: '故障', maintenance: '维护中' }
  const statusColors = { online: '#67C23A', offline: '#909399', fault: '#F56C6C', maintenance: '#E6A23C' }
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: deviceStats.value.by_status.map((item) => ({
        name: statusLabels[item.status] || item.status,
        value: item.count,
        itemStyle: { color: statusColors[item.status] },
      })),
    }],
  })
}

onMounted(async () => {
  try {
    const [overviewData, callData, patrolData, deviceData] = await Promise.all([
      getOverview(),
      getCallStats({ days: 7 }),
      getPatrolStats(),
      getDeviceStatusSummary(),
    ])
    overview.value = overviewData
    callStats.value = callData
    patrolStats.value = patrolData
    deviceStats.value = deviceData
    await nextTick()
    renderCallChart()
    renderDeviceChart()
  } catch {
    // 数据加载失败，页面显示默认值
  }
})
</script>

<style lang="scss" scoped>
.dashboard {
  .kpi-row {
    margin-bottom: 20px;
  }

  .kpi-card {
    .kpi-content {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .kpi-value {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
    }
    .kpi-title {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }
    .kpi-footer {
      margin-top: 12px;
      font-size: 12px;
      color: #909399;
      border-top: 1px solid #ebeef5;
      padding-top: 8px;
    }
  }

  .chart-row {
    margin-bottom: 20px;
  }

  .patrol-stats {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    padding: 20px;
  }

  .patrol-info p {
    margin: 8px 0;
    font-size: 14px;
    color: #606266;
  }

  .occupancy-info {
    padding: 20px;
  }
}
</style>
