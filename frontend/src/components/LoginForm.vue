<template>
    <div class="login-container">
        <h2>Вход в систему</h2>
        <form @submit.prevent="onSubmit">
            <div>
                <label for="email">Email:</label>
                <input v-model="email" type="email" id="email" required>
            </div>
            <div>
                <label for="password">Пароль:</label>
                <input v-model="password" type="password" id="password" required>
            </div>
            <button type="submit">Войти</button>
            <p v-if="error" class="error">{{ error }}</p>
        </form>
    </div>
</template>

<script>
import {useAuthStore} from "../store";

export default {
    name: 'LoginForm',
    data() {
        return {
            email: '',
            password: '',
            error: '',
        }
    },
    setup() {
        const authStore = useAuthStore()
        return {authStore}
    },
    methods: {
        async onSubmit() {
            try {
                await this.authStore.login(this.email, this.password)
                this.$router.push('/tasks')
            } catch (err) {
                this.error = 'Неверный email или пароль'
            }
        }
    }
}
</script>

<style scoped>
.login-container {
    width: 300px;
    margin: 100px auto;
}

.error {
    color: red;
    margin-top: 10px;
}
</style>