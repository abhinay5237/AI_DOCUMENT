import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

export const analyzeDocuments = async (driveLink) => {
  const formData = new FormData();
  formData.append("drive_link", driveLink);

  const response = await axios.post(`${API_BASE}/analyze`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};