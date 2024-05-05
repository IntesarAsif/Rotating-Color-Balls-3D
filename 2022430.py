import numpy as np
import moderngl
from _example import Example
from pyrr import Matrix44


class Scissor(Example):
    gl_version = (3, 3)
    title = "Scissor"
    resizable = True
    aspect_ratio = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330

                in vec3 in_vert;

                uniform mat4 model;
                uniform mat4 projection;

                void main() {
                    gl_Position = projection * model * vec4(in_vert, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330

                out vec4 fragColor;
                uniform vec4 color;

                void main() {
                    fragColor = color;
                }
            ''',
        )

        # Create a sphere geometry
        num_segments = 30
        vertices = []
        for lat in range(num_segments // 2):
            theta = lat * np.pi / num_segments
            for lon in range(num_segments):
                phi = lon * 2 * np.pi / num_segments
                x = np.sin(theta) * np.cos(phi)
                y = np.sin(theta) * np.sin(phi)
                z = np.cos(theta)
                vertices.extend([x, y, z])
        vbo = self.ctx.buffer(np.array(vertices, dtype='f4'))
        self.vao = self.ctx.vertex_array(self.prog, [(vbo, '3f', 'in_vert')])

        self.num_balls = 4  # Number of round balls
        self.ball_positions = [(0, 0, -3), (0, 0, -5), (0, 0, -7), (0, 0, -9)]  # Positions of the balls
        self.ball_colors = [(1.0, 0.0, 0.0, 0.0),  # Red, Green, Blue, White
                            (0.0, 1.0, 0.0, 0.0),
                            (0.0, 0.0, 1.0, 0.0),
                            (1.0, 1.0, 1.0, 1.0)]
        self.rotations = [0.0] * self.num_balls  # Rotation angles for each ball

    def resize(self, width, height):
        self.aspect_ratio = width / height

    def render(self, time: float, frame_time: float):
        """Render the coloring screen with rotating round balls"""

        # Enable depth testing
        self.ctx.enable(moderngl.DEPTH_TEST)

        # Perspective projection matrix
        projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 100.0)

        for i in range(self.num_balls):
            # Rotate the round ball
            model = Matrix44.from_translation(self.ball_positions[i]) * Matrix44.from_eulers((self.rotations[i], self.rotations[i], self.rotations[i]))

            # Render the coloring screen with each ball
            self.prog['projection'].write(projection.astype('f4').tobytes())

            # Set color and model transformation
            self.prog['color'].value = self.ball_colors[i]
            self.prog['model'].write(model.astype('f4').tobytes())

            # Render the round ball
            self.vao.render(mode=moderngl.TRIANGLE_STRIP)

            # Increment rotation for next frame
            self.rotations[i] += 0.01


if __name__ == '__main__':
    Scissor.run()
