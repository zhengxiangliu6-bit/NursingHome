<template>
  <div>
    <el-card>
      <template #header>
        <div class="card-header">
          <span>信息发布</span>
          <el-button type="primary" @click="dialogVisible = true">发布通知</el-button>
        </div>
      </template>
      <el-table :data="notices" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" />
        <el-table-column prop="notice_type" label="类型" width="100" />
        <el-table-column prop="author_name" label="作者" width="100" />
        <el-table-column prop="is_published" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'" size="small">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="!row.is_published" type="success" size="small" @click="handlePublish(row.id)">发布</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新建通知" width="600">
      <el-form :model="form" label-width="80px">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.notice_type">
            <el-option label="通知公告" value="announcement" />
            <el-option label="制度规范" value="policy" />
            <el-option label="活动通知" value="activity" />
            <el-option label="紧急通报" value="emergency" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="5" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getNotices, createNotice, publishNotice } from '@/api/campus'
import { ElMessage } from 'element-plus'

const notices = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const form = reactive({ title: '', notice_type: 'announcement', content: '' })

async function loadData() {
  loading.value = true
  try {
    const data = await getNotices()
    notices.value = data.results || data
  } finally { loading.value = false }
}

async function handleCreate() {
  await createNotice(form)
  ElMessage.success('通知创建成功')
  dialogVisible.value = false
  loadData()
}

async function handlePublish(id) {
  await publishNotice(id)
  ElMessage.success('已发布')
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
</style>
