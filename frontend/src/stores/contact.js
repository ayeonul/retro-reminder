import { defineStore } from 'pinia'
import apiClient from '../api/client'


export const useContactStore = defineStore('contact', {
  state: () => ({
    selectedIds: [],
    contacts: []
  }),
  actions: {
    async loadContacts() {
      const { data } = await apiClient.get('/contacts')
      this.contacts = data
    },
    async addContact(name, phone) {
      const { data } = await apiClient.post('/contacts', { name: name.trim(), phone: phone.trim() })
      this.contacts.push(data)
    },
    toggleSelection(id) {
      this.selectedIds = this.selectedIds.includes(id)
        ? this.selectedIds.filter((selectedId) => selectedId !== id)
        : [...this.selectedIds, id]
    },
    async deleteSelected() {
      await Promise.all(this.selectedIds.map((id) => apiClient.delete(`/contacts/${id}`)))
      this.contacts = this.contacts.filter((contact) => !this.selectedIds.includes(contact.id))
      this.selectedIds = []
    },
    clearSelection() {
      this.selectedIds = []
    }
  }
})
