import { defineStore } from 'pinia'
import apiClient from '../api/client'


export const useMemoStore = defineStore('memo', {
  state: () => ({
    selectedIds: [],
    memos: []
  }),
  actions: {
    async loadMemos() {
      const { data } = await apiClient.get('/memos')
      this.memos = data
    },
    async addMemo(title, content = '') {
      const { data } = await apiClient.post('/memos', { title: title.trim(), content: content.trim() })
      this.memos.push(data)
    },
    toggleSelection(id) {
      this.selectedIds = this.selectedIds.includes(id)
        ? this.selectedIds.filter((selectedId) => selectedId !== id)
        : [...this.selectedIds, id]
    },
    async deleteSelected() {
      await Promise.all(this.selectedIds.map((id) => apiClient.delete(`/memos/${id}`)))
      this.memos = this.memos.filter((memo) => !this.selectedIds.includes(memo.id))
      this.selectedIds = []
    },
    clearSelection() {
      this.selectedIds = []
    }
  }
})
