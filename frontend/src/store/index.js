import { defineStore } from "pinia";
import apiClient from "../services/api";

const API_URL = import.meta.env.VUE_APP_API_URL || "/api";

export const useUserStore = defineStore("users", {
    state: () => ({
        users: [],
    }),
    actions: {
        async fetchUsers() {
            const response = await apiClient.get("/users/");
            this.users = response.data;
        },
    },
});

export const useAuthStore = defineStore("auth", {
    state: () => ({
        accessToken: localStorage.getItem("access_token") || null,
        refreshToken: localStorage.getItem("refresh_token") || null,
        user: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.accessToken,
        avatarUrl: (state) => state.user?.avatar_url || null,
    },
    actions: {
        async login(email, password) {
            try {
                const response = await apiClient.post("/token/", {
                    email,
                    password,
                });
                this.accessToken = response.data.access;
                this.refreshToken = response.data.refresh;
                localStorage.setItem("access_token", this.accessToken);
                localStorage.setItem("refresh_token", this.refreshToken);
                await this.fetchUser();
            } catch (error) {
                throw error;
            }
        },
        async logout() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
        },
        async fetchUser() {
            try {
                const response = await apiClient.get("/users/me/");
                this.user = response.data;
            } catch (error) {
                await this.logout();
                throw error;
            }
        },
        async refreshTokens() {
            try {
                const response = await apiClient.post("/token/refresh", {
                    refresh: this.refreshToken,
                });
                this.accessToken = response.data.access;
                localStorage.setItem("access_token", this.accessToken);
            } catch (error) {
                await this.logout();
                throw error;
            }
        },
        async uploadAvatar(file) {
            try {
                const formData = new FormData();
                formData.append("avatar", file);

                await apiClient.patch("/users/me/", formData, {
                    headers: {
                        "Content-Type": "multipart/form-data",
                    },
                });
                await this.fetchUser();
            } catch (error) {
                throw error;
            }
        },
    },
});

export const useTaskStore = defineStore("tasks", {
    state: () => ({
        tasks: [],
        openTasks: [],
        closedTasks: [],
        statuses: [],
        priorities: [],
        projects: [],
        currentProjectId: "all",
        comments: [],
    }),
    actions: {
        async fetchInitialData() {
            const [statusesRes, prioritiesRes, projectsRes] = await Promise.all(
                [
                    apiClient.get("/tasks/statuses/"),
                    apiClient.get("/tasks/priorities"),
                    apiClient.get("/tasks/projects/"),
                ]
            );
            this.statuses = statusesRes.data;
            this.priorities = prioritiesRes.data;
            this.projects = projectsRes.data;
        },
        async fetchTasks(projectId = "all") {
            const response = await apiClient.get(
                `/tasks/tasks/?project=${projectId}`
            );
            this.tasks = response.data;
            await this.fetchClosedTasks(projectId);
            await this.fetchOpenTasks(projectId);
            this.currentProjectId = projectId;
        },
        async fetchOpenTasks(projectId = "all") {
            const response = await apiClient.get(
                `/tasks/tasks/?project=${projectId}&not_status=4`
            );
            this.openTasks = response.data;
        },
        async fetchClosedTasks(projectId = "all") {
            const response = await apiClient.get(
                `/tasks/tasks/?project=${projectId}&status=4`
            );
            this.closedTasks = response.data;
        },
        async createTask(taskData) {
            const payload = { ...taskData };
            if (payload.due_date)
                payload.due_date = new Date(payload.due_date).toISOString();
            const response = await apiClient.post("/tasks/tasks/", payload);
            await this.fetchTasks(this.currentProjectId);
            return response;
        },
        async updateTask(id, taskData, byIssueId = false) {
            const url = byIssueId
                ? `/tasks/tasks/${id}/?by_issue_id=1`
                : `/tasks/tasks/${id}/`;
            const payload = { ...taskData };
            if (payload.due_date)
                payload.due_date = new Date(payload.due_date).toISOString();
            await apiClient.patch(url, payload);
            await this.fetchTasks(this.currentProjectId);
        },
        async deleteTask(id, byIssueId = false) {
            try {
                const url = `/tasks/tasks/${id}/?by_issue_id=1`;
                await apiClient.delete(url);
                await this.fetchTasks(this.currentProjectId);
            } catch (error) {
                console.error("Ошибка при удалении задачи:", error);
                throw error;
            }
        },
        async fetchProjects() {
            const response = await apiClient.get("/tasks/projects/");
            this.projects = response.data;
        },
        async createProject(projectData) {
            await apiClient.post("/tasks/projects/", projectData);
            await this.fetchProjects();
        },
        async updateProject(id, projectData) {
            await apiClient.put(`/tasks/projects/${id}/`, projectData);
            await this.fetchProjects();
        },
        async deleteProject(id) {
            await apiClient.delete(`/tasks/projects/${id}/`);
            await this.fetchProjects();
        },
        async fetchComments(taskId, byIssueId = false) {
            try {
                const url = byIssueId
                    ? `/tasks/comments/?task_issue_id=${taskId}`
                    : `/tasks/comments/?task=${taskId}`;
                const response = await apiClient.get(url);
                this.comments = response.data;
            } catch (error) {
                console.error("Ошибка при получении комментариев:", error);
                throw error;
            }
        },
        async createComment(commentData) {
            try {
                const formData = new FormData();
                if (commentData.by_issue_id) {
                    formData.append("task_issue_id", commentData.task);
                } else {
                    formData.append("task", commentData.task);
                }
                formData.append("text", commentData.text);
                if (commentData.attachment) {
                    formData.append("attachment", commentData.attachment);
                }

                await apiClient.post("/tasks/comments/", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
                await this.fetchComments(
                    commentData.task,
                    commentData.by_issue_id
                );
            } catch (error) {
                console.error("Ошибка при создании комментария:", error);
                throw error;
            }
        },
        async deleteComment(id, taskId, byIssueId = false) {
            const url = `/tasks/comments/${id}/`;
            await apiClient.delete(url);
            await this.fetchComments(taskId, byIssueId);
        },
    },
});
