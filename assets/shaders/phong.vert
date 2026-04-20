#version 330 core

// Vertex attributes from the mesh buffers.
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

// Data passed to the fragment shader.
out vec3 FragPos;
out vec3 Normal;

// Scene and camera transforms.
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    FragPos = vec3(model * vec4(aPos, 1.0));
    
    // Use inverse-transpose to keep normals correct under non-uniform scaling.
    Normal = mat3(transpose(inverse(model))) * aNormal;
    
    gl_Position = projection * view * vec4(FragPos, 1.0);
}
