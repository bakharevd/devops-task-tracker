<template>
    <HeaderLayout/>
    <router-view/>
</template>

<script>
import HeaderLayout from "./components/layouts/HeaderLayout.vue";

export default {
    name: 'App',
    components: {
        HeaderLayout
    }
}
</script>

<style scoped>
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

a {
    text-decoration: none;
    color: inherit;
}

button {
    font-family: inherit;
}
</style>
