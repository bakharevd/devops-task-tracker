import {defineStore} from "pinia";
import apiClient from "../services/api";

const API_URL = import.meta.env.VUE_APP_API_URL || '/api'


export const useUserStore = defineStore('users', {
    state: () => ({
        users: []
    }),
    actions: {
        async fetchUsers() {
            const response = await apiClient.get('/users/')
            this.users = response.data
        }
    }
})


export const useAuthStore = defineStore('auth', {
    state: () => ({
        accessToken: localStorage.getItem('access_token') || null,
        refreshToken: localStorage.getItem('refresh_token') || null,
        user: null,
    }),
    actions: {
        async login(email, password) {
            try {
                const response = await apiClient.post('/token/', {
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
                const response = await apiClient.get('/users/me/')
                this.user = response.data
            } catch (error) {
                await this.logout()
                throw error
            }
        },
        async refreshTokens() {
            try {
                const response = await apiClient.post('/token/refresh', {
                    refresh: this.refreshToken
                })
                this.accessToken = response.data.access
                localStorage.setItem('access_token', this.accessToken)
            } catch (error) {
                await this.logout()
                throw error
            }
        }
    }
})

export const useTaskStore = defineStore('tasks', {
    state: () => ({
        tasks: [],
        statuses: [],
        priorities: [],
        projects: [],
        currentProjectId: 'all',
        comments: []
    }),
    actions: {
        async fetchInitialData() {
            const [statusesRes, prioritiesRes, projectsRes] = await Promise.all([
                apiClient.get('/tasks/statuses/'),
                apiClient.get('/tasks/priorities'),
                apiClient.get('/tasks/projects/')
            ])
            this.statuses = statusesRes.data
            this.priorities = prioritiesRes.data
            this.projects = projectsRes.data
        },
        async fetchTasks(projectId = 'all') {
            const response = await apiClient.get(`/tasks/tasks/?project=${projectId}`)
            this.tasks = response.data
            this.currentProjectId = projectId
        },
        async createTask(taskData) {
            await apiClient.post('/tasks/tasks/', taskData)
            await this.fetchTasks(this.currentProjectId)
        },
        async updateTask(id, taskData) {
            await apiClient.patch(`/tasks/tasks/${id}`, taskData)
            await this.fetchTasks(this.currentProjectId)
        },
        async deleteTask(id) {
            await apiClient.delete(`/tasks/tasks/${id}/`)
            await this.fetchTasks(this.currentProjectId)
        },
        async fetchProjects() {
            const response = await apiClient.get('/tasks/projects/')
            this.projects = response.data
        },
        async createProject(projectData) {
            await apiClient.post('/tasks/projects/', projectData)
            await this.fetchProjects()
        },
        async updateProject(id, projectData) {
            await apiClient.patch(`/tasks/projects/${id}/`, projectData)
            await this.fetchProjects()
        },
        async deleteProject(id) {
            await apiClient.delete(`/tasks/projects/${id}/`)
            await this.fetchProjects()
        },
        async fetchComments(taskId) {
            const response = await apiClient.get(`/tasks/comments/?task=${taskId}`)
            this.comments = response.data
        },
        async createComment(commentData) {
            const formData = new FormData()
            formData.append('task_id', commentData.task)
            formData.append('text', commentData.text)
            if (commentData.attachment) {
                formData.append('attachment', commentData.attachment)
            }
            await apiClient.post('/tasks/comments/', formData, {
                headers: {'Content-Type': 'multipart/form-data'}
            })
            await this.fetchComments(commentData.task)
        },
        async deleteComment(id, taskId) {
            await apiClient.delete(`/tasks/comments/${id}/`)
            await this.fetchComments(taskId)
        }
    }
})
