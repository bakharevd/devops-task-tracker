import {defineStore} from "pinia";
import axios from "axios";

const API_URL = import.meta.env.VUE_APP_API_URL || '/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
        user: null,
    }),
    actions: {
        async login(email, password) {
            try {
                const response = await axios.post(`${API_URL}/token/`, {
                    email,
                    password
                })
                this.accessToken = response.data.access
                this.refreshToken = response.data.refresh
                localStorage.setItem('access_token', this.accessToken)
                localStorage.setItem('refresh_token', this.refreshToken)
                await this.fetchUser()
            } catch (error) {
                throw error
            }
        },
        async logout() {
            this.accessToken = null
            this.refreshToken = null
            this.user = null
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
        },
        async fetchUser() {
            try {
                const response = await axios.get(`${API_URL}/users/me/`, {
                    headers: {
                        Authorization: `Bearer ${this.accessToken}`
                    }
                })
                this.user = response.data
            } catch (error) {
                this.logout()
                throw error
            }
        },
        async refreshTokens() {
            try {
                const response = await axios.post(`${API_URL}/token/refresh`, {
                    refresh: this.refreshToken
                })
                this.accessToken = response.data.access
                localStorage.setItem('access_token', this.accessToken)
            } catch (error) {
                this.logout()
                throw error
            }
        }
    }
})

export const useTaskStore = defineStore('tasks', {
    state: () => ({
        tasks: [],
        statuses: [],
        priorities: []
    }),
    actions: {
        async fetchInitialData() {
            const authStore = useAuthStore()
            const headers = {
                Authorization: `Bearer ${authStore.accessToken}`
            }
            const [statusesRes, prioritiesRes] = await Promise.all([
                axios.get(`${API_URL}/tasks/statuses/`, {headers}),
                axios.get(`${API_URL}/tasks/priorities`, {headers})
            ])
            this.statuses = statusesRes.data
            this.priorities = prioritiesRes.data
        },
        async fetchTasks() {
            const authStore = useAuthStore()
            const headers = {
                Authorization: `Bearer ${authStore.accessToken}`
            }
            const response = await axios.get(`${API_URL}/tasks/tasks/`, {headers})
            this.tasks = response.data
        },
        async createTask(taskData) {
            const authStore = useAuthStore()
            const headers = {
                Authorization: `Bearer ${authStore.accessToken}`
            }
            const response = await axios.post(`${API_URL}/tasks/tasks/`, taskData, {headers})
            await this.fetchTasks()
        },
        async updateTask(id, taskData) {
            const authStore = useAuthStore()
            const headers = {
                Authorization: `Bearer ${authStore.accessToken}`
            }
            await axios.patch(`${API_URL}/tasks/tasks/${id}`, taskData, {headers})
            await this.fetchTasks()
        },
        async deleteTask(id) {
            const authStore = useAuthStore()
            const headers = {
                Authorization: `Bearer ${authStore.accessToken}`
            }
            const response = await axios.delete(`${API_URL}/tasks/tasks/${id}/`, {headers})
            await this.fetchTasks()
        }
    }
})
