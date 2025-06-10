<template>
    <div class="task-detail-container">
        <div v-if="loading">
            Загрузка задачи…
        </div>

        <div v-else>
            <h2>Задача: {{ task.title }}</h2>
            <p><strong>ID задачи:</strong> {{ task.issue_id }}</p>
            <p><strong>Описание:</strong> {{ task.description || '—' }}</p>
            <p><strong>Проект:</strong> {{ task.project?.name || '—' }}</p>
            <p><strong>Статус:</strong> {{ findStatusName(task.status) }}</p>
            <p><strong>Приоритет:</strong> {{ findPriorityLevel(task.priority) }}</p>
            <p><strong>Исполнитель:</strong> {{ task.assignee?.username || '—' }}</p>
            <p><strong>Создатель:</strong> {{ task.creator.username }}</p>
            <p><strong>Дедлайн:</strong> {{ formatDate(task.due_date) }}</p>

            <section class="comments-section">
                <h3>Комментарии</h3>

                <div class="comment-form">
                    <textarea
                        v-model="newComment.text"
                        placeholder="Добавить комментарий..."
                    ></textarea>
                    <input type="file" @change="onFileChanged"/>
                    <button @click="submitComment">Отправить</button>
                </div>

                <ul v-if="comments.length">
                    <li v-for="c in comments" :key="c.id">
                        <p>
                            <strong>{{ c.author.username }}</strong>
                            ({{ formatDate(c.created_at) }})
                        </p>
                        <p>{{ c.text }}</p>
                        <p v-if="c.attachment">
                            Вложение:
                            <a :href="attachmentUrl(c.attachment)" target="_blank">
                                Скачать
                            </a>
                        </p>
                        <button
                            v-if="isCommentAuthor(c.author.username)"
                            @click="deleteComment(c.id)"
                        >
                            Удалить
                        </button>
                    </li>
                </ul>
                <p v-else>Комментариев нет.</p>
            </section>

            <button @click="goBack">← К задачам проекта</button>
        </div>
    </div>
</template>

<script>
import {computed, onMounted, ref} from 'vue'
import {useAuthStore, useTaskStore} from '../store'
import {useRoute, useRouter} from 'vue-router'
import apiClient from '../services/api.js'

export default {
    name: 'TaskDetail',
    setup() {
        const taskStore = useTaskStore()
        const authStore = useAuthStore()
        const route = useRoute()
        const router = useRouter()

        const taskId = computed(() => route.params.id)
        const task = ref(null)
        const loading = ref(true)

        const comments = computed(() => taskStore.comments)
        const newComment = ref({text: '', attachment: null})
        const error = ref('')

        onMounted(async () => {
            try {
                await authStore.fetchUser()
                const response = await apiClient.get(`/tasks/tasks/${taskId.value}/?by_issue_id=1`)
                task.value = response.data
                await taskStore.fetchInitialData()
                await taskStore.fetchComments(taskId.value, true)
            } catch (e) {
                console.error('Ошибка при загрузке задачи:', e)
                error.value = 'Не удалось загрузить задачу'
            } finally {
                loading.value = false
            }
        })

        function findStatusName(statusId) {
            const st = taskStore.statuses.find(s => s.id === statusId)
            return st ? st.name : ''
        }

        function findPriorityLevel(priorityId) {
            const p = taskStore.priorities.find(p => p.id === priorityId)
            return p ? p.level : ''
        }

        function formatDate(dt) {
            if (!dt) return '—'
            return dt.replace('T', ' ').substring(0, 16)
        }

        function onFileChanged(event) {
            newComment.value.attachment = event.target.files[0]
        }

        async function submitComment() {
            if (!newComment.value.text.trim() && !newComment.value.attachment) {
                return
            }
            try {
                await taskStore.createComment({
                    task: taskId.value,
                    text: newComment.value.text,
                    attachment: newComment.value.attachment,
                    by_issue_id: true
                })
                newComment.value.text = ''
                newComment.value.attachment = null
            } catch (e) {
                console.error('Ошибка при отправке комментария:', e)
            }
        }

        function attachmentUrl(path) {
            return path
        }

        function isCommentAuthor(authorUsername) {
            return authStore.user && authStore.user.username === authorUsername
        }

        async function deleteComment(commentId) {
            if (confirm('Удалить комментарий?')) {
                await taskStore.deleteComment(commentId, taskId.value, true)
            }
        }

        function goBack() {
            const projectId = task.value?.project?.id
            if (projectId) {
                router.push({
                    name: 'TaskListByProject',
                    params: {projectId: projectId}
                })
            } else {
                router.push({name: 'ProjectList'})
            }
        }

        return {
            task,
            comments,
            newComment,
            loading,
            error,
            findStatusName,
            findPriorityLevel,
            formatDate,
            onFileChanged,
            submitComment,
            attachmentUrl,
            isCommentAuthor,
            deleteComment,
            goBack
        }
    }
}
</script>

<style scoped>
.task-detail-container {
    max-width: 800px;
    margin: 30px auto;
    padding: 0 20px;
}

.comments-section {
    margin-top: 30px;
}

.comment-form {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 20px;
}

.comment-form textarea {
    width: 100%;
    height: 80px;
    padding: 6px;
    box-sizing: border-box;
}

.comment-form input[type="file"] {
    width: 100%;
}

.comment-form button {
    align-self: flex-start;
    padding: 6px 12px;
}

.comments-section ul {
    list-style: none;
    padding: 0;
}

.comments-section li {
    margin-bottom: 15px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.comments-section li p {
    margin: 4px 0;
}

.comments-section li button {
    margin-top: 5px;
    padding: 4px 8px;
    cursor: pointer;
}

button {
    margin-top: 20px;
    padding: 6px 12px;
    cursor: pointer;
}
</style>
