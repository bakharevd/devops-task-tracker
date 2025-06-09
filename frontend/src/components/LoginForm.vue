<template>
    <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div class="w-full max-w-md bg-white shadow-xl rounded-2xl p-8">
            <Image
                src="/logo.png"
                alt="DevOps Task Tracker"
                width="256"
                class="flex justify-center mb-5"
            />
            <h2 class="text-2xl font-bold text-center mb-6">
                Вход в систему
            </h2>

            <form @submit.prevent="onSubmit" class="space-y-5">
                <div>
                    <label
                        for="email"
                        class="block text-sm font-medium text-gray-700 mb-1"
                        >Электронная почта</label
                    >
                    <InputText
                        id="email"
                        v-model="email"
                        class="w-full"
                        placeholder="ceo@yandex.ru"
                    />
                </div>

                <div>
                    <label
                        for="password"
                        class="block text-sm font-medium text-gray-700 mb-1"
                        >Пароль</label
                    >
                    <Password
                        inputId="password"
                        v-model="password"
                        :feedback="false"
                        toggleMask
                        class="w-full"
                        inputClass="w-full"
                        placeholder="••••••••"
                    />
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200">
                    Войти
                </button>

                <p v-if="error" class="text-red-500 text-sm text-center mt-2">
                    {{ error }}
                </p>
            </form>
        </div>
    </div>
</template>

<script>
import { useAuthStore } from "../store";

export default {
    name: "LoginForm",
    data() {
        return {
            email: "",
            password: "",
            error: "",
        };
    },
    setup() {
        const authStore = useAuthStore();
        return { authStore };
    },
    methods: {
        async onSubmit() {
            try {
                await this.authStore.login(this.email, this.password);
                this.$router.push("/tasks");
            } catch (err) {
                this.error = "Неверный email или пароль";
            }
        },
    },
};
</script>
