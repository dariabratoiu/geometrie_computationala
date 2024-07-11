import tkinter as tk 
from tkinter import Canvas
import random
import numpy as np

class TriangulationApp:
    def __init__(self, root):
        # Constructor
        self.root = root
        self.root.title("Point Location in triangulations")

        # Set-up unde vor fi desenate punctele/linii etc
        self.canvas = Canvas(root, width=1000, height=800, bg="white")
        self.canvas.pack()

        # punctele, date despre triangulari, triunghiurile colorate
        self.puncte = []
        self.triangulare = []
        self.triunghiuri_colorate = {}

        # Butoanele
        self.btn_random = tk.Button(root, text="Generare puncte", command=self.generare_puncte)
        self.btn_random.pack(side=tk.LEFT)
        self.btn_triangulate = tk.Button(root, text="Triangulare", command=self.triangulare_puncte)
        self.btn_triangulate.pack(side=tk.LEFT)
        self.btn_add_point = tk.Button(root, text="Adauga punct", command=self.add_punct_mode)
        self.btn_add_point.pack(side=tk.LEFT)

        # variabila care arata daca s-a apasat "Adauga punct"
        self.add_point_active = False

        # click stanga pe canvas pentru adaugare ppunct
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    #BACKEND
    def generare_puncte(self):
        # Generare puncte in canvas
        self.puncte = [(random.randint(100, 900), random.randint(100, 700)) for _ in range(1000)]
        self.triangulare = []  # sterge triangulare daca exista
        self.triunghiuri_colorate = {}  # sterge triunghiuri daca exista
        self.clear_canvas()
        self.vizualiz_puncte()

    #FRONTEND
    def clear_canvas(self):
        # sterge puncte & triangulari & triunghiuri 
        self.canvas.delete("all")

    #FRONTEND
    def vizualiz_puncte(self):
        # Deseneaza punctele
        for punct in self.puncte:
            self.canvas.create_oval(punct[0]-3, punct[1]-3, punct[0]+3, punct[1]+3, fill="black")
        # Face & deseneaza triangularea daca exista deja
        if self.triangulare:
            self.vizualiz_triangulare()

    #FRONTEND
    def triangulare_puncte(self):
        # triangularea se face doar daca sunt minim 3 puncte 
        if len(self.puncte) < 3:
            return
        self.triangulare = self.bowyer_watson(self.puncte) 
        self.clear_canvas()
        self.vizualiz_triangulare()
        self.vizualiz_puncte()

    #FRONTEND
    def vizualiz_triangulare(self):
        # Desenarea triunghiurilor obtinute la triangulare
        for triunghi in self.triangulare:
            pts = np.array(triunghi)
            fill_color = self.triunghiuri_colorate.get(tuple(map(tuple, pts)), '') 
            self.canvas.create_polygon([tuple(pts[0]), tuple(pts[1]), tuple(pts[2])], 
                                       outline='black', fill=fill_color, width=2)

    #BACKEND
    def add_punct_mode(self):
        # S-a apasat "Adaugă punct"
        self.add_point_active = True

    #BACKEND
    def on_canvas_click(self, event):
        # ce se intampla cand apas pe canvas
        if self.add_point_active:
            punct = (event.x, event.y)
            self.puncte.append(punct)
            self.coloreaza_triunghi(punct)
            self.add_point_active = False  # Dezactivvare "Adauga punct"

    # RONTEND
    def coloreaza_triunghi(self, punct):
        # Gasesc & colorez triunghiul care contine punctul
        if not self.triangulare:
            return
        for triunghi in self.triangulare:
            if self.is_point_in_tri(punct, triunghi):
                # culoare random
                color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), 
                                                     random.randint(0, 255))
                self.triunghiuri_colorate[tuple(map(tuple, triunghi))] = color
                self.clear_canvas()
                self.vizualiz_triangulare()
                self.vizualiz_puncte()
                self.canvas.create_oval(punct[0]-3, punct[1]-3, punct[0]+3, punct[1]+3, fill="black")
                break

    # BACKEND
    def is_point_in_tri(self, punct, triunghi):
        def arie_triunghi(p1, p2, p3):
            return abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2
        
        ariaTriunghiuluiMare = arie_triunghi(triunghi[0], triunghi[1], triunghi[2])
        aria1 = arie_triunghi(punct, triunghi[1], triunghi[2])
        aria2 = arie_triunghi(triunghi[0], punct, triunghi[2])
        aria3 = arie_triunghi(triunghi[0], triunghi[1], punct)
        
        return aria1 + aria2 + aria3 - ariaTriunghiuluiMare == 0

    #BACKEND
    def bowyer_watson(self, puncte):
        # Creare super triunghi care cuprinde toate punctele
        super_triunghi = [(-10000, -10000), (10000, -10000), (0, 10000)]
        triangulare = [super_triunghi]

        def cerc_circumscris(tri):
            # cercul circumscris triunghiului
            ax, ay = tri[0]
            bx, by = tri[1]
            cx, cy = tri[2]
            # Coordonatele cercului circumscris triunghiului
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
            uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d
            r = np.sqrt((ux - ax) ** 2 + (uy - ay) ** 2)
            return (ux, uy), r

        for punct in puncte:
            bad_triangles = []
            for tri in triangulare:
                (ux, uy), r = cerc_circumscris(tri)
                # Verific daca punctul este in cercul circumscris al triunghiului
                if np.sqrt((ux - punct[0]) ** 2 + (uy - punct[1]) ** 2) < r:
                    bad_triangles.append(tri)

            # Poligon cu triunghiurile "rele"
            poligon = []
            for tri in bad_triangles:
                for latura in [(tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])]:
                    shared = False
                    for other in bad_triangles:
                        if other == tri:
                            continue
                        if latura[0] in other and latura[1] in other:
                            shared = True
                            break
                    if not shared:
                        poligon.append(latura)

            # Stergem bad trianlges din triangulare
            for tri in bad_triangles:
                triangulare.remove(tri)

            # Traingulam cu muchiile din poligon
            for latura in poligon:
                new_tri = (latura[0], latura[1], punct)
                triangulare.append(new_tri)

        # Stergere triunghiuri care au de-a face cu super triunghiul
        triangulare = [tri for tri in triangulare if not any(varf in tri for varf in super_triunghi)]
        return triangulare



if __name__ == "__main__":
    root = tk.Tk()
    app = TriangulationApp(root)
    root.mainloop()
