import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
});

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/upload_resume", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return data;
};

export const fetchSavedJobs = async () => {
  const { data } = await api.get("/saved-jobs");
  return data.jobs;
};

export const saveJob = async (job) => {
  await api.post("/saved-jobs", job);
};

export default api;
