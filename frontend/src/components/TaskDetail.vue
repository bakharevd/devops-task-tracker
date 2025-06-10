<template>
    <div class="min-h-screen flex flex-col items-center px-4 inset-x-0 top-0">
        <div v-if="loading" class="w-full max-w-7xl mt-8">
            <div v-for="i in 3" :key="i" class="mb-4">
                <Skeleton height="2rem" class="mb-2" />
                <Skeleton height="2rem" class="mb-2" />
                <Skeleton height="2rem" />
            </div>
        </div>

        <div v-else class="card w-full max-w-7xl mt-8">
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center gap-4">
                    <Button
                        @click="goBack"
                        icon="pi pi-arrow-left"
                        severity="secondary"
                        text
                        rounded
                        raised
                    />
                    <h2 class="text-2xl font-semibold m-0">{{ task.title }}</h2>
                </div>
                <div class="flex gap-2">
                    <Button
                        @click="goEdit(task.issue_id)"
                        icon="pi pi-pencil"
                        severity="info"
                        rounded
                        raised
                        class="flex items-center gap-2"
                    >
                        <i class="pi pi-pencil"></i>
                    </Button>
                    <Button
                        @click="onDelete(task.issue_id)"
                        icon="pi pi-trash"
                        severity="danger"
                        rounded
                        raised
                        class="flex items-center gap-2"
                    >
                        <i class="pi pi-trash"></i>
                    </Button>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="card">
                    <h3 class="text-xl font-semibold mb-4">
                        Основная информация
                    </h3>
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >ID задачи</label
                            >
                            <div class="text-lg">{{ task.issue_id }}</div>
                        </div>
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Проект</label
                            >
                            <div class="text-lg">
                                {{ task.project?.name || "—" }}
                            </div>
                        </div>
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Статус</label
                            >
                            <Tag
                                v-if="findStatusName(task.status)"
                                :severity="
                                    uiStyles.getStatusStyle(
                                        findStatusName(task.status)
                                    ).severity
                                "
                                :value="
                                    uiStyles.getStatusStyle(
                                        findStatusName(task.status)
                                    ).label
                                "
                                :icon="
                                    uiStyles.getStatusStyle(
                                        findStatusName(task.status)
                                    ).icon
                                "
                            />
                        </div>
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Приоритет</label
                            >
                            <Tag
                                v-if="findPriorityLevel(task.priority)"
                                :severity="
                                    uiStyles.getPriorityStyle(
                                        findPriorityLevel(task.priority)
                                    ).severity
                                "
                                :value="
                                    uiStyles.getPriorityStyle(
                                        findPriorityLevel(task.priority)
                                    ).label
                                "
                                :icon="
                                    uiStyles.getPriorityStyle(
                                        findPriorityLevel(task.priority)
                                    ).icon
                                "
                                rounded
                            />
                        </div>
                        <div
                            v-tooltip.top="
                                `${task.assignee?.last_name} ${
                                    task.assignee?.first_name
                                }\n(${task.assignee?.position?.name || ''})`
                            "
                        >
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Исполнитель</label
                            >
                            <div
                                v-if="task.assignee"
                                class="flex items-center gap-2"
                            >
                                <Avatar
                                    :image="task.assignee?.avatar_url"
                                    shape="circle"
                                />
                                <span
                                    >{{ task.assignee?.last_name }}
                                    {{ task.assignee?.first_name }}</span
                                >
                            </div>
                            <div v-else>—</div>
                        </div>
                        <div
                            v-tooltip.top="
                                `${task.creator?.last_name} ${
                                    task.creator?.first_name
                                }\n(${task.creator?.position?.name || ''})`
                            "
                        >
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Создатель</label
                            >
                            <div class="flex items-center gap-2">
                                <Avatar
                                    :image="task.creator?.avatar_url"
                                    shape="circle"
                                />
                                <span
                                    >{{ task.creator?.last_name }}
                                    {{ task.creator?.first_name }}</span
                                >
                            </div>
                        </div>
                        <div>
                            <label
                                class="block text-sm font-medium text-gray-600 mb-1"
                                >Дедлайн</label
                            >
                            <div class="text-lg">
                                {{ formatDate(task.due_date) }}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <h3 class="text-xl font-semibold mb-4">Описание</h3>
                    <div class="prose max-w-none" v-html="task.description || 'Описание отсутствует'"></div>
                </div>
            </div>

            <div class="card mt-6 mb-6">
                <h3 class="text-xl font-semibold mb-4 max-w-3xl mx-auto">
                    Комментарии
                </h3>

                <div v-if="comments.length" class="space-y-4 max-w-3xl mx-auto">
                    <div
                        v-for="c in comments"
                        :key="c.id"
                        class="card p-4 border border-gray-200 rounded-lg"
                        :class="{
                            'bg-blue-50 border-blue-200': isCommentAuthor(
                                c.author.username
                            ),
                            'hover:border-gray-300 transition-colors':
                                !isCommentAuthor(c.author.username),
                        }"
                    >
                        <div class="flex justify-between items-start mb-2">
                            <div class="flex items-center gap-2">
                                <Avatar
                                    :image="c.author?.avatar_url"
                                    shape="circle"
                                    v-tooltip.top="
                                        `${c.author?.last_name} ${
                                            c.author?.first_name
                                        }\n(${c.author?.position?.name || ''})`
                                    "
                                />
                                <div>
                                    <div class="font-medium">
                                        {{ c.author?.last_name }}
                                        {{ c.author?.first_name }}
                                        <span class="text-gray-500"
                                            >({{
                                                c.author?.position?.name
                                            }})</span
                                        >
                                    </div>
                                    <div class="text-sm text-gray-500">
                                        {{ formatDate(c.created_at) }}
                                    </div>
                                </div>
                            </div>
                            <Button
                                v-if="isCommentAuthor(c.author.username)"
                                @click="deleteComment(c.id)"
                                icon="pi pi-trash"
                                severity="danger"
                                text
                                rounded
                            />
                        </div>
                        <div class="prose max-w-none mb-2" v-html="c.text"></div>
                        <div v-if="c.attachment" class="mt-2">
                            <a
                                :href="attachmentUrl(c.attachment)"
                                target="_blank"
                                class="flex items-center gap-2 text-primary hover:underline"
                            >
                                <i class="pi pi-paperclip"></i>
                                <span>Скачать вложение</span>
                            </a>
                        </div>
                    </div>
                </div>

                <div v-else class="text-center text-gray-500 py-4">
                    Комментариев пока нет
                </div>

                <div class="mt-6 max-w-3xl mx-auto">
                    <div class="flex flex-col gap-4">
                        <Editor
                            v-model="newComment.text"
                            editorStyle="height: 200px"
                            :pt="{
                                toolbar: { class: 'border-none' },
                                content: { class: 'border border-gray-300 rounded-lg' }
                            }"
                        />
                        <div class="flex items-center gap-4">
                            <Button
                                @click="handleCommentSubmit"
                                icon="pi pi-send"
                                severity="info"
                                label="Отправить"
                                class="flex-1"
                                raised
                                :disabled="!newComment.text.trim()"
                            />
                            <FileUpload
                                mode="basic"
                                :auto="true"
                                accept="image/*,application/pdf,.doc,.docx,.xls,.xlsx,.txt,.zip,.rar,.7z,.mov,.mp3,.wav"
                                :maxFileSize="10000000"
                                @select="onFileChanged"
                                chooseIcon="pi pi-paperclip"
                                chooseLabel="Прикрепить файл"
                            />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { computed, onMounted, ref } from "vue";
import { useAuthStore, useTaskStore } from "../store";
import { useUiStyleStore } from "../store/uiStyles";
import { useRoute, useRouter } from "vue-router";
import apiClient from "../services/api.js";

export default {
    name: "TaskDetail",
    setup() {
        const taskStore = useTaskStore();
        const authStore = useAuthStore();
        const uiStyles = useUiStyleStore();
        const route = useRoute();
        const router = useRouter();

        const taskId = computed(() => route.params.id);
        const task = ref(null);
        const loading = ref(true);

        const comments = computed(() => taskStore.comments);
        const newComment = ref({ text: "", attachment: null });
        const error = ref("");

        const handleTaskUpdate = async (updatedTask) => {
            try {
                await taskStore.updateTask(taskId.value, updatedTask, true);
                const response = await apiClient.get(
                    `/tasks/tasks/${taskId.value}/?by_issue_id=1`
                );
                task.value = response.data;
            } catch (e) {
                console.error("Ошибка при обновлении задачи:", e);
                if (e.response) {
                    error.value =
                        e.response.data.detail || "Не удалось обновить задачу";
                } else if (e.request) {
                    error.value = "Нет ответа от сервера";
                } else {
                    error.value = "Не удалось обновить задачу";
                }
            }
        };

        onMounted(async () => {
            try {
                await authStore.fetchUser();
                const response = await apiClient.get(
                    `/tasks/tasks/${taskId.value}/?by_issue_id=1`
                );
                task.value = response.data;
                await taskStore.fetchInitialData();
                await taskStore.fetchComments(taskId.value, true);
            } catch (e) {
                console.error("Ошибка при загрузке задачи:", e);
                if (e.response) {
                    error.value =
                        e.response.data.detail || "Не удалось загрузить задачу";
                } else if (e.request) {
                    error.value = "Нет ответа от сервера";
                } else {
                    error.value = "Не удалось загрузить задачу";
                }
            } finally {
                loading.value = false;
            }
        });

        function findStatusName(statusId) {
            const st = taskStore.statuses.find((s) => s.id === statusId);
            return st ? st.name : "";
        }

        function findPriorityLevel(priorityId) {
            const p = taskStore.priorities.find((p) => p.id === priorityId);
            return p ? p.level : "";
        }

        function formatDate(dt) {
            if (!dt) return "—";
            return dt.replace("T", " ").substring(0, 16);
        }

        function onFileChanged(event) {
            newComment.value.attachment = event.files[0];
        }

        const handleCommentSubmit = async () => {
            if (!newComment.value.text.trim()) {
                error.value = "Введите текст комментария";
                return;
            }
            try {
                const formData = new FormData();
                formData.append("task_issue_id", taskId.value);
                formData.append("text", newComment.value.text);
                if (newComment.value.attachment) {
                    formData.append("attachment", newComment.value.attachment);
                }

                await apiClient.post("/tasks/comments/", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });

                newComment.value = { text: "", attachment: null };
                await taskStore.fetchComments(taskId.value, true);
                error.value = "";
            } catch (e) {
                console.error("Ошибка при создании комментария:", e);
                if (e.response) {
                    error.value =
                        e.response.data.detail ||
                        "Не удалось создать комментарий";
                } else if (e.request) {
                    error.value = "Нет ответа от сервера";
                } else {
                    error.value = "Не удалось создать комментарий";
                }
            }
        };

        function attachmentUrl(path) {
            return path;
        }

        function isCommentAuthor(authorUsername) {
            return authStore.user && authStore.user.username === authorUsername;
        }

        async function deleteComment(commentId) {
            if (confirm("Удалить комментарий?")) {
                await taskStore.deleteComment(commentId, taskId.value, true);
            }
        }

        function goBack() {
            const projectId = task.value?.project?.id;
            if (projectId) {
                router.push({
                    name: "TaskListByProject",
                    params: { projectId: projectId },
                });
            } else {
                router.push({ name: "ProjectList" });
            }
        }

        function goEdit(id) {
            router.push({ name: "TaskEdit", params: { id } });
        }

        async function onDelete(id) {
            if (confirm("Удалить задачу?")) {
                try {
                    await taskStore.deleteTask(id);
                    goBack();
                } catch (e) {
                    console.error(e);
                }
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
            handleCommentSubmit,
            attachmentUrl,
            isCommentAuthor,
            deleteComment,
            goBack,
            goEdit,
            onDelete,
            uiStyles,
        };
    },
};
</script>

<style scoped>
.prose {
    color: #334155;
    line-height: 1.625;
    word-wrap: break-word;
    overflow-wrap: break-word;
    white-space: pre-wrap;
}

.prose p {
    margin-bottom: 1rem;
}

.prose p:last-child {
    margin-bottom: 0;
}

.prose :deep(p) {
    margin-bottom: 1rem;
}

.prose :deep(p:last-child) {
    margin-bottom: 0;
}

.prose :deep(h1),
.prose :deep(h2),
.prose :deep(h3),
.prose :deep(h4),
.prose :deep(h5),
.prose :deep(h6) {
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    font-weight: 600;
}

.prose :deep(ul),
.prose :deep(ol) {
    margin-top: 1rem;
    margin-bottom: 1rem;
    padding-left: 1.5rem;
}

.prose :deep(li) {
    margin-bottom: 0.5rem;
}

.prose :deep(blockquote) {
    margin: 1rem 0;
    padding-left: 1rem;
    border-left: 4px solid #e2e8f0;
    color: #64748b;
}
</style>
