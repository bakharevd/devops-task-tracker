<template>
    <nav>
        <a
            href="/admin/"
            target="_blank"
            rel="noopener"
            class="admin-link"
            v-if="isAdmin"
        >Админка</a>
        <a
            href="/logout/"
            rel="noopener"
            class="admin-link"
            v-if="isAuthrized"
        >Выйти</a>
    </nav>
</template>

<script>
import {computed} from 'vue'
import {useAuthStore} from "../../store";

export default {
    setup() {
        const authStore = useAuthStore()
        const isAdmin = computed(() => authStore.user && authStore.user.is_superuser === true)
        const isAuthrized = computed(() => authStore.user)

        return {
            isAdmin,
            isAuthrized
        }
    }
}

</script>

<style scoped>
.admin-link {
    margin-left: 20px;
    text-decoration: none;
    color: #007bff;
}
</style>