import pygame

pygame.init()

windowWidth = 800
windowHeight = 800

windowRes = (windowWidth, windowHeight)
screen = pygame.display.set_mode(windowRes)

pygame.display.set_caption("Stack!")

PHEIGHT = 2.5 #platform height
ISO_MULTIPLIER = 10

class Platform:
    #the height of the cube is always the same, the only thing that changes is the base's dimensions
    def __init__(self, width, depth, color=None):
        self.width = width
        self.depth = depth
        self.height = PHEIGHT
        self.color = color
        self.colors = [(255,0,0), (0,255,0), (0,0,255)]
        self.vertices = self.defineVertices()
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()

    def defineVertices(self):
        vertices = [(x, y, z)
                    for x in (0, self.width)
                    for y in (0, self.depth)
                    for z in (0, self.height)]
        
        return vertices
    
    def defineEdges(self):
        edges = [(i, j) 
            for i, v1 in enumerate(self.vertices) 
            for j, v2 in enumerate(self.vertices) 
            if i < j and sum(a != b for a, b in zip(v1, v2)) == 1]
        
        return edges
    
    def defineVisibleEdges(self):
        visible_edges = [
            (1,3),
            (1,5),
            (2,3),
            (2,6),
            (3,7),
            (4,5),
            (4,6),
            (5,7),
            (6,7)
        ]
        return visible_edges

    def defineFaces(self):
        visible_faces = [
            (1,7,1,5),
            (2,3,7,6),
            (4,5,7,6)
        ]
        return visible_faces
    
    def convertToIsometric(self, x, y ,z):
        iso_x = x - y
        iso_y = (x + y) / 2 - z
        return iso_x, iso_y
    
    def draw(self):
        vertices = [self.vertices[i] for i in self.faces[0]]
        iso_vertices = [self.convertToIsometric(x * ISO_MULTIPLIER, y * ISO_MULTIPLIER, z * ISO_MULTIPLIER) for x,y,z in vertices]
        iso_vertices = [(x + windowWidth // 2, y + windowHeight//2) for x, y in iso_vertices]

        pygame.draw.polygon(screen, self.colors[0], iso_vertices)
        
        '''for face, color in zip(self.faces, self.colors):
            # Get the 3D coordinates of the vertices making up the face
            vertices = [self.vertices[i] for i in face]
            
            # Convert the 3D vertices to 2D isometric coordinates
            iso_vertices = [self.convertToIsometric(x * ISO_MULTIPLIER, y * ISO_MULTIPLIER, z * ISO_MULTIPLIER) 
                            for x, y, z in vertices]
            
            # Offset the vertices to the center of the screen
            iso_vertices = [(x + windowWidth // 2, y + windowHeight // 2) for x, y in iso_vertices]
            
            # Draw the polygon (face) using the converted isometric coordinates
            pygame.draw.polygon(screen, color, iso_vertices)'''
        for edge in self.edges:
            #get the 3D coords from 2 vertices
            x1, y1, z1 = self.vertices[edge[0]]
            x2, y2, z2 = self.vertices[edge[1]]
            
            #apply isometric projection to both vertices

            iso_x1, iso_y1 = self.convertToIsometric(x1 * ISO_MULTIPLIER, y1 * ISO_MULTIPLIER, z1 * ISO_MULTIPLIER)
            iso_x2, iso_y2 = self.convertToIsometric(x2 * ISO_MULTIPLIER, y2 * ISO_MULTIPLIER, z2 * ISO_MULTIPLIER)
            
            iso_x1 += windowWidth // 2
            iso_y1 += windowHeight // 2
            iso_x2 += windowWidth // 2
            iso_y2 += windowHeight // 2

            pygame.draw.line(screen, (255, 255, 255), (iso_x1, iso_y1), (iso_x2, iso_y2), 2)

plat = Platform(10, 10)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    plat.draw()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
