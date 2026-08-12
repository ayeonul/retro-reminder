import { defineStore } from 'pinia'
import apiClient from '../api/client'


function formatDate(year, month, day) {
  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function mapSchedule(schedule) {
  const [year, month, day] = schedule.date.split('-').map(Number)

  return {
    ...schedule,
    time: schedule.time.slice(0, 5),
    year,
    month,
    day,
    alertEnabled: schedule.alert_enabled
  }
}

export const useReminderStore = defineStore('reminder', {
  state: () => ({
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    selectedDay: new Date().getDate(),
    schedules: []
  }),
  getters: {
    selectedSchedules: (state) => state.schedules.filter((schedule) => (
      schedule.year === state.year && schedule.month === state.month && schedule.day === state.selectedDay
    )),
    selectedDateLabel: (state) => {
      const weekdays = ['일', '월', '화', '수', '목', '금', '토']
      const weekday = weekdays[new Date(state.year, state.month - 1, state.selectedDay).getDay()]

      return `${state.year}년 ${state.month}월 ${state.selectedDay}일 (${weekday})`
    }
  },
  actions: {
    async loadSchedules() {
      const lastDay = new Date(this.year, this.month, 0).getDate()
      const { data } = await apiClient.get('/schedules', {
        params: {
          from: formatDate(this.year, this.month, 1),
          to: formatDate(this.year, this.month, lastDay)
        }
      })
      this.schedules = data.map(mapSchedule)
    },
    selectDay(day) {
      this.selectedDay = day
    },
    async moveMonth(offset) {
      const date = new Date(this.year, this.month - 1 + offset, 1)
      this.year = date.getFullYear()
      this.month = date.getMonth() + 1
      this.selectedDay = 1
      await this.loadSchedules()
    },
    async goToToday() {
      const today = new Date()
      this.year = today.getFullYear()
      this.month = today.getMonth() + 1
      this.selectedDay = today.getDate()
      await this.loadSchedules()
    },
    async addSchedule(title, time) {
      const { data } = await apiClient.post('/schedules', {
        date: formatDate(this.year, this.month, this.selectedDay),
        time: time || '09:00',
        title: title.trim(),
        alert_enabled: false
      })
      this.schedules.push(mapSchedule(data))
    },
    async toggleScheduleAlert(id) {
      const schedule = this.schedules.find((item) => item.id === id)
      if (!schedule) return
      const { data } = await apiClient.patch(`/schedules/${id}`, { alert_enabled: !schedule.alertEnabled })
      Object.assign(schedule, mapSchedule(data))
    },
    async deleteSchedule(id) {
      await apiClient.delete(`/schedules/${id}`)
      this.schedules = this.schedules.filter((schedule) => schedule.id !== id)
    }
  }
})
