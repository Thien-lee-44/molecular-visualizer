#version 330 core

// Dữ liệu đầu vào từ VBO (Vertex Buffer Object)
layout (location = 0) in vec3 aPos;    // Tọa độ đỉnh
layout (location = 1) in vec3 aNormal; // Vector pháp tuyến

// Dữ liệu xuất ra để truyền cho Fragment Shader
out vec3 FragPos;
out vec3 Normal;

// Ma trận biến đổi từ Scene Graph và Camera
uniform mat4 model;      // Ma trận toàn cục của đối tượng (World Matrix)
uniform mat4 view;       // Ma trận góc nhìn (Camera)
uniform mat4 projection; // Ma trận phối cảnh (Perspective)

void main()
{
    // 1. Tính toán vị trí của đỉnh trong không gian thế giới
    FragPos = vec3(model * vec4(aPos, 1.0));
    
    // 2. Chuyển đổi vector pháp tuyến sang không gian thế giới
    // Sử dụng ma trận nghịch đảo chuyển vị để tránh làm méo pháp tuyến khi Scale không đồng đều
    Normal = mat3(transpose(inverse(model))) * aNormal;
    
    // 3. Tính toán vị trí cuối cùng trên màn hình
    gl_Position = projection * view * vec4(FragPos, 1.0);
}