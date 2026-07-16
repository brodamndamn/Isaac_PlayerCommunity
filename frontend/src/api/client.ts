import axios from "axios";

const client = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});

// 请求拦截器：自动附加 JWT token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：401 时清除 token 并跳转登录页
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("access_token");
    }
    return Promise.reject(err);
  },
);

export default client;
