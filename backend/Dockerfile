# Sử dụng phiên bản Node.js 24.14.0 Alpine siêu nhẹ
FROM node:24.14.0-alpine

# Cài đặt các công cụ biên dịch C++ cơ bản. 
# Do SQLite3 sử dụng Native Bindings (viết bằng C++), môi trường Alpine đôi khi cần bộ công cụ này để biên dịch nội bộ thành công.
RUN apk add --no-cache python3 make g++

# Đặt thư mục làm việc trong container
WORKDIR /app

# Chỉ copy file quản lý thư viện trước để tận dụng Docker Cache
COPY package.json package-lock.json ./

# Cài đặt thư viện: Lệnh --omit=dev sẽ bỏ qua toàn bộ gói jest, eslint, supertest 
RUN npm ci --omit=dev

# Copy toàn bộ mã nguồn còn lại của backend vào container
COPY . .

# Khai báo các biến môi trường
ENV NODE_ENV=production
ENV PORT=3000

# Mở cổng 3000
EXPOSE 3000

# Khởi chạy server 
CMD ["node", "server.js"]