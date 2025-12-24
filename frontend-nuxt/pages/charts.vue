<script setup>
import { 
  ChartBarIcon, 
  BuildingOfficeIcon,
  BriefcaseIcon,
  CalendarIcon,
  MapPinIcon,
  ChatBubbleLeftIcon
} from '@heroicons/vue/24/outline'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Filler
} from 'chart.js'
import { Bar, Line, Pie, Doughnut, Radar } from 'vue-chartjs'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  ArcElement,
  RadialLinearScale,
  Filler
)

const activeTab = ref('org')
const loading = ref(false)
const error = ref(null)
const rawData = ref(null)
const monthOptions = ref([])
const selectedMonth = ref('')
const chartType = ref('horizontalBar') // Default to horizontalBar

const tabs = [
  { id: 'org', name: '機關開缺數', icon: BuildingOfficeIcon, endpoint: '/api/job_openings_chart' },
  { id: 'sysnam', name: '職系開缺數', icon: BriefcaseIcon, endpoint: '/api/job_openings_chart_by_sysnam' },
  { id: 'daily', name: '每日開缺數', icon: CalendarIcon, endpoint: '/api/job_openings_daily_chart' },
  { id: 'workplace', name: '地點開缺數', icon: MapPinIcon, endpoint: '/api/job_openings_workplace_chart' },
  { id: 'comments', name: '熱門留言職缺', icon: ChatBubbleLeftIcon, endpoint: '/api/job_openings_commentscount_chart' }
]

// Chart Options
const chartOptions = computed(() => {
  return {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: chartType.value === 'horizontalBar' ? 'y' : 'x',
    plugins: {
      legend: {
        position: 'top',
        display: true
      },
      title: {
        display: true,
        text: getChartTitle()
      }
    }
  }
})

const getChartTitle = () => {
  const tab = tabs.find(t => t.id === activeTab.value)
  return tab ? tab.name : ''
}

const fetchChartData = async () => {
  loading.value = true
  error.value = null
  rawData.value = null
  
  try {
    const tab = tabs.find(t => t.id === activeTab.value)
    const params = {}
    if (selectedMonth.value && activeTab.value !== 'comments') {
      params.month = selectedMonth.value
    }
    
    const response = await $fetch(tab.endpoint, { params })
    rawData.value = response
    
    if (response.month_options) {
      monthOptions.value = response.month_options
      if (!selectedMonth.value) {
        selectedMonth.value = response.month
      }
    }
  } catch (err) {
    error.value = '無法取得圖表資料'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const changeTab = (tabId) => {
  activeTab.value = tabId
  // Reset chart type based on tab
  if (tabId === 'daily') {
    chartType.value = 'line'
  } else if (tabId === 'comments') {
    chartType.value = 'list'
  } else {
    chartType.value = 'horizontalBar' // Enforce horizontal bar for others
  }
  fetchChartData()
}

// Computed Data for Chart.js
const chartData = computed(() => {
  if (!rawData.value) return null

  let labels = []
  let data = []
  let label = '數量'

  if (activeTab.value === 'org') {
    labels = rawData.value.org_names
    data = rawData.value.job_counts
    label = '機關開缺數'
  } else if (activeTab.value === 'sysnam') {
    labels = rawData.value.sys_names
    data = rawData.value.job_counts
    label = '職系開缺數'
  } else if (activeTab.value === 'daily') {
    labels = rawData.value.dates
    data = rawData.value.job_counts
    label = '每日開缺數'
  } else if (activeTab.value === 'workplace') {
    labels = rawData.value.workplace_types
    data = rawData.value.job_counts
    label = '地點開缺數'
  }

  const backgroundColors = [
    'rgba(54, 162, 235, 0.6)',
    'rgba(255, 99, 132, 0.6)',
    'rgba(255, 206, 86, 0.6)',
    'rgba(75, 192, 192, 0.6)',
    'rgba(153, 102, 255, 0.6)',
    'rgba(255, 159, 64, 0.6)'
  ]

  return {
    labels,
    datasets: [
      {
        label,
        backgroundColor: chartType.value === 'pie' || chartType.value === 'doughnut' ? backgroundColors : 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1,
        data
      }
    ]
  }
})

// Computed Data for Table
const tableData = computed(() => {
  if (!chartData.value || !chartData.value.labels || !chartData.value.datasets[0].data) return []
  
  const labels = chartData.value.labels
  const data = chartData.value.datasets[0].data
  const total = data.reduce((a, b) => a + b, 0)
  
  return labels.map((label, index) => {
    const value = data[index]
    const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : '0.0'
    return {
      label,
      value,
      percentage
    }
  })
})

onMounted(() => {
  fetchChartData()
})

// SEO
useSeoMeta({
  title: '統計圖表 - 開放事求人',
  description: '查看公務人員職缺的各項統計數據，包含機關、職系、地點等開缺排行。',
  ogTitle: '統計圖表 - 開放事求人',
  ogDescription: '查看公務人員職缺的各項統計數據，包含機關、職系、地點等開缺排行。',
})
</script>

<template>
  <div class="page-container">
    <!-- Page Header -->
    <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 flex items-center gap-2 mb-2">
          <ChartBarIcon class="w-8 h-8 text-primary-600" />
          統計圖表
        </h1>
        <p class="text-slate-600">瀏覽所有職缺的統計數據</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex flex-wrap gap-2 mb-8 border-b border-slate-200 pb-2">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="changeTab(tab.id)"
        :class="[
          'flex items-center gap-2 px-4 py-2.5 rounded-t-lg font-medium transition-all text-sm sm:text-base border-b-2',
          activeTab === tab.id 
            ? 'border-primary-600 text-primary-700 bg-primary-50' 
            : 'border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50'
        ]"
      >
        <component :is="tab.icon" class="w-5 h-5" :class="activeTab === tab.id ? 'text-primary-600' : 'text-slate-400'" />
        {{ tab.name }}
      </button>
    </div>

    <!-- Controls -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex flex-wrap items-center gap-4">
      <!-- Month Selector -->
      <div v-if="activeTab !== 'comments' && monthOptions.length > 0" class="flex items-center gap-2">
        <label class="font-medium text-slate-700 text-sm">月份：</label>
        <select 
          v-model="selectedMonth" 
          @change="fetchChartData"
          class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 outline-none text-sm"
        >
          <option v-for="opt in monthOptions" :key="opt.value" :value="opt.value">
            {{ opt.label }}
          </option>
        </select>
      </div>
    </div>

    <!-- Content -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-slate-400">
      <div class="w-10 h-10 border-4 border-slate-200 border-l-primary-500 rounded-full animate-spin mb-4"></div>
      <p class="font-medium">正在載入圖表資料...</p>
    </div>

    <div v-else-if="error" class="bg-red-50 border border-red-100 text-red-600 p-6 rounded-xl text-center">
      {{ error }}
    </div>

    <div v-else-if="rawData" class="space-y-6">
      
      <!-- Chart Rendering -->
      <div class="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 min-h-[500px]">
        <div v-if="activeTab !== 'comments'" class="h-[500px] w-full">
          <ClientOnly>
            <Bar v-if="chartType === 'bar' || chartType === 'horizontalBar'" :data="chartData" :options="chartOptions" />
            <Pie v-else-if="chartType === 'pie'" :data="chartData" :options="chartOptions" />
            <Doughnut v-else-if="chartType === 'doughnut'" :data="chartData" :options="chartOptions" />
            <Line v-else-if="chartType === 'line'" :data="chartData" :options="chartOptions" />
          </ClientOnly>
        </div>

        <!-- Comments List (Special Case) -->
        <div v-else>
          <h3 class="text-lg font-bold mb-4">熱門留言職缺</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="job in rawData.most_commented_jobs" :key="job.id" class="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow group">
              <div class="flex justify-between items-start mb-2">
                <h4 class="font-bold text-lg text-primary-600 group-hover:text-primary-700">
                  <NuxtLink :to="`/job/${job.id}`">
                    {{ job.title }}
                  </NuxtLink>
                </h4>
                <span class="bg-emerald-100 text-emerald-700 px-2 py-1 rounded-lg text-sm font-bold flex items-center gap-1">
                  <ChatBubbleLeftIcon class="w-4 h-4" />
                  {{ job.comment_count }}
                </span>
              </div>
              <div class="text-slate-600 text-sm mb-1 font-medium">{{ job.org_name }}</div>
              <div class="text-slate-500 text-xs flex items-center gap-2">
                <CalendarIcon class="w-3 h-3" />
                {{ job.date_from }} ~ {{ job.date_to }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Data Table -->
      <div v-if="activeTab !== 'comments' && activeTab !== 'daily' && tableData.length > 0" class="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div class="p-4 border-b border-slate-100 bg-slate-50">
          <h3 class="font-bold text-slate-800">詳細數據表格</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="text-white uppercase bg-primary-600 border-b border-primary-700">
              <tr>
                <th class="px-6 py-4 font-bold rounded-tl-lg">排名</th>
                <th class="px-6 py-4 font-bold">名稱</th>
                <th class="px-6 py-4 font-bold text-right">開缺數</th>
                <th class="px-6 py-4 font-bold text-right rounded-tr-lg">佔比</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(row, index) in tableData" :key="index" class="hover:bg-slate-50 transition-colors">
                <td class="px-6 py-4 font-medium text-slate-900">{{ index + 1 }}</td>
                <td class="px-6 py-4 text-slate-700">{{ row.label }}</td>
                <td class="px-6 py-4 text-right font-bold text-primary-600">{{ row.value }}</td>
                <td class="px-6 py-4 text-right text-slate-500">{{ row.percentage }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>
