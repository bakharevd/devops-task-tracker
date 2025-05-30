<template>
    <div class="project-form-container">
        <h2>Новый проект</h2>
        <form @submit.prevent="onSubmit">
            <div>
                <label for="name">Название проекта:</label>
                <input
                    v-model="form.name"
                    type="text"
                    id="name"
                    placeholder="Введите название"
                    required
                />
            </div>
            <div>
                <label for="description">Описание:</label>
                <textarea
                    v-model="form.description"
                    id="description"
                    placeholder="Опционально: описание проекта"
                ></textarea>
            </div>
            <button type="submit">Создать</button>
            <button @click="goBack" type="button">Отмена</button>
        </form>
        <p v-if="error" class="error">{{ error }}</p>
    </div>
</template>

<script>
import {ref} from 'vue'
import {useTaskStore} from '../store'
import {useRouter} from 'vue-router'

export default {
    name: 'ProjectForm',
    setup() {
        const taskStore = useTaskStore()
        const router = useRouter()
        const form = ref({
            name: '',
            description: ''
        })
        const error = ref('')

        async function onSubmit() {
            if (!form.value.name.trim()) {
                error.value = 'Нельзя создавать проект без названия'
                return
            }
            try {
                await taskStore.createProject({
                    name: form.value.name,
                    description: form.value.description
                })
                router.push({name: 'ProjectList'})
            } catch (err) {
                error.value = 'Ошибка при создании проекта'
                console.error(err)
            }
        }

        function goBack() {
            router.push({name: 'ProjectList'})
        }

        return {
            form,
            error,
            onSubmit,
            goBack
        }
    }
}
</script>

<style scoped>
.project-form-container {
    max-width: 500px;
    margin: 50px auto;
    padding: 0 20px;
}

.project-form-container div {
    margin-bottom: 15px;
}

.project-form-container input,
.project-form-container textarea {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    margin-right: 10px;
    padding: 6px 12px;
    cursor: pointer;
}

.error {
    color: red;
    margin-top: 10px;
}
</style>
