<template>
    <div class="min-h-screen flex flex-col items-center px-4 inset-x-0 top-0">
        <div class="card w-full max-w-3xl mt-8">
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
                    <h2 class="text-2xl font-semibold m-0">
                        {{ isEdit ? 'Редактирование проекта' : 'Новый проект' }}
                    </h2>
                </div>
            </div>

            <form @submit.prevent="onSubmit" class="flex flex-col gap-6">
                <div class="field">
                    <label for="name" class="block text-sm font-medium text-gray-600 mb-1">Название проекта</label>
                    <InputText
                        v-model="form.name"
                        id="name"
                        placeholder="Введите название"
                        class="w-full"
                        required
                    />
                </div>

                <div class="field">
                    <label for="description" class="block text-sm font-medium text-gray-600 mb-1">Описание</label>
                    <Editor
                        v-model="form.description"
                        editorStyle="height: 200px"
                        :pt="{
                            toolbar: { class: 'border-none' },
                            content: { class: 'border border-gray-300 rounded-lg' }
                        }"
                    />
                </div>

                <div class="field">
                    <label for="members" class="block text-sm font-medium text-gray-600 mb-1">Участники проекта</label>
                    <MultiSelect
                        v-model="form.members_ids"
                        :options="users"
                        optionLabel="fullName"
                        optionValue="id"
                        placeholder="Выберите участников"
                        class="w-full"
                        :pt="{
                            root: { class: 'w-full' },
                            label: { class: 'flex items-center gap-2' }
                        }"
                    >
                        <template #option="slotProps">
                            <div class="flex items-center gap-2">
                                <Avatar
                                    :image="slotProps.option.avatar_url"
                                    shape="circle"
                                    size="small"
                                />
                                <div>
                                    <div>{{ slotProps.option.fullName }}</div>
                                    <div class="text-sm text-gray-500">{{ slotProps.option.email }}</div>
                                </div>
                            </div>
                        </template>
                    </MultiSelect>
                </div>

                <div class="field">
                    <label for="code" class="block text-sm font-medium text-gray-600 mb-1">Код проекта</label>
                    <InputText
                        v-model="form.code"
                        id="code"
                        placeholder="Короткий код (например, ASD)"
                        class="w-full"
                        required
                    />
                </div>

                <div class="flex justify-end gap-2 mt-4">
                    <Button
                        type="button"
                        @click="goBack"
                        label="Отмена"
                        severity="secondary"
                        outlined
                    />
                    <Button
                        type="submit"
                        :label="isEdit ? 'Сохранить' : 'Создать'"
                        severity="success"
                        :loading="loading"
                    />
                </div>
            </form>

            <Message v-if="error" severity="error" :closable="false" class="mt-4">
                {{ error }}
            </Message>
        </div>
    </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore, useTaskStore, useUserStore } from '../store'
import { useRoute, useRouter } from 'vue-router'
import apiClient from "../services/api"

export default {
    name: 'ProjectForm',
    setup() {
        const taskStore = useTaskStore()
        const userStore = useUserStore()
        const authStore = useAuthStore()
        const route = useRoute()
        const router = useRouter()

        const isEdit = computed(() => Boolean(route.params.projectId))
        const projectId = computed(() => route.params.projectId)

        const form = ref({
            name: '',
            description: '',
            members_ids: [],
            code: ''
        })
        const error = ref('')
        const loading = ref(false)

        const users = computed(() => 
            userStore.users.map(user => ({
                ...user,
                fullName: `${user.last_name} ${user.first_name}`
            }))
        )

        onMounted(async () => {
            try {
                loading.value = true
                await authStore.fetchUser()
                await userStore.fetchUsers()
                await taskStore.fetchProjects()

                if (isEdit.value) {
                    const response = await apiClient.get(`/tasks/projects/${projectId.value}/`)
                    const data = response.data
                    form.value.name = data.name || ''
                    form.value.description = data.description || ''
                    form.value.members_ids = data.members.map(u => u.id)
                    form.value.code = data.code || ''
                }
            } catch (e) {
                console.error('Ошибка при инициализации компонента:', e)
                error.value = 'Не удалось загрузить данные формы'
            } finally {
                loading.value = false
            }
        })

        async function onSubmit() {
            if (!form.value.name.trim()) {
                error.value = 'Укажите название проекта'
                return
            }
            if (!form.value.code.trim()) {
                error.value = 'Укажите код проекта'
                return
            }

            loading.value = true
            error.value = ''
            const payload = {
                name: form.value.name,
                description: form.value.description,
                members_ids: form.value.members_ids,
                code: form.value.code
            }
            try {
                if (isEdit.value) {
                    await taskStore.updateProject(projectId.value, payload)
                } else {
                    await taskStore.createProject(payload)
                }
                router.push({ name: 'ProjectList' })
            } catch (err) {
                console.error('Ошибка при сохранении проекта:', err)
                error.value = 'Не удалось сохранить проект'
            } finally {
                loading.value = false
            }
        }

        function goBack() {
            router.push({ name: 'ProjectList' })
        }

        return {
            form,
            users,
            isEdit,
            onSubmit,
            goBack,
            error,
            loading
        }
    }
}
</script>

<style scoped>
.field {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}
</style>

