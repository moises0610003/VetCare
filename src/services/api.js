const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";
async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || "No fue posible completar la operación");
  return body;
}
export const api = {
  get: path => request(path), post: (path, data) => request(path, { method:"POST", body:JSON.stringify(data) }),
  put: (path,data) => request(path,{method:"PUT",body:JSON.stringify(data)}), remove:path=>request(path,{method:"DELETE"})
};
