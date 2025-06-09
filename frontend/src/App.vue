<template>
    <HeaderLayout />
    <router-view />
</template>

<script>
import HeaderLayout from "./components/layouts/HeaderLayout.vue";

export default {
    name: "App",
    components: {
        HeaderLayout,
    },
};
</script>

<style>
@import "tailwindcss";

body {
    margin: 0;
    padding: 0;
}

body,
html {
    font-family: "Segoe UI", "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    font-weight: 400;
}

strong,
b {
    font-weight: 700;
}

em,
i {
    font-style: italic;
}

code,
pre,
kbd,
samp {
    font-family: "Consolas", "Courier New", monospace;
}

a {
    text-decoration: none;
    color: inherit;
}

button {
    font-family: inherit;
}
</style>
