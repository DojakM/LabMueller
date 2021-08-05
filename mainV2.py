import tkinter.font as font
from tkinter import *
import classsheet as cs
import Crossings as cross


def checkMutants(dubs):
    with open("mutants.txt", 'r') as file:
        mutationPositions = []
        for line in file:
            line = line.strip()
            entry = line.split("   ")
            mutationName = entry[0]
            mutationPositions = entry[1:]
            for i in dubs[1:]:
                if i == mutationName:
                    return mutationPositions
        return []
class RegionWindow:
    seq = ""

    def __init__(self, protein):
        self.load_protein(protein)

        # create a window that has ...
        root = Tk()
        root.attributes('-fullscreen', True)

        # scaling of the window
        heigth = root.winfo_screenheight()
        width = root.winfo_screenwidth()

        # Scrollable Window Scale
        canvasWidth = int(width-20)
        canvasHeigth = int(heigth/2)
        self.factor = canvasWidth / len(self.seq)

        scroll_frame = Frame(root)
        self.constructs = cs.Construct_reader(protein).constructs
        draw_field = Canvas(scroll_frame, height=canvasHeigth, width=canvasWidth)
        draw_field.create_rectangle(10, 25, self.factor * len(self.seq), 100, fill='lightgrey')
        draw_field.create_text(10, 10, anchor=NW, text=protein)

        val = 0
        if len(self.constructs) > 1:
            for construct in self.constructs:
                begin = 0
                print(construct)
                end = len(self.seq)
                dub = construct.split(" ")
                if len(dub) > 1:
                    val = val + 1
                    if re.match(".*H+.*[A-Z,a-z]+.*", dub[1]):
                        end = len(self.seq)
                    if len(dub) == 2:
                        if dub[1].__contains__("-"):
                            startEnd = dub[1].split("-")
                            begin = int(startEnd[0])
                            end = int(startEnd[1])
                    elif len(dub) > 2:
                        if dub[2] == "stop":
                            begin = int(dub[1])

                        else:
                            startEnd = dub[1].split("-")
                            begin = int(startEnd[0])
                            end = int(startEnd[1])

                    mutants = checkMutants(dub)
                    if len(mutants)>0:
                        for mutation in mutants:
                            draw_field.create_line(10 + int(mutation)*self.factor, 100 * val + 25,
                                                   10 + int(mutation)*self.factor,
                                                   100 * val + 75, fill = "red", width = 0.1)

                        draw_field.create_text(10 + int(mutation)*self.factor, 100 * val + 20,anchor = "e", text=
                                               "Mutations @ " + " ,".join(mutants))

                    # writing the constructs name
                    draw_field.create_text(10, 100 * val + 10, anchor=NW, text=construct)

                    # drawing of the construct
                    draw_field.create_line(begin * self.factor + 10, 100 * val + 50, end * self.factor, 100 * val +
                                           50)
                    draw_field.create_line(begin * self.factor + 10, 100 * val + 25, begin * self.factor + 10,
                                           100 * val + 75)
                    draw_field.create_line(end * self.factor, 100 * val + 25, end * self.factor, 100 * val + 75)

        scroll_bar = Scrollbar(scroll_frame, orient="vertical", command=draw_field.yview, width=32,
                               elementborderwidth=56)
        scrollable_frame = Frame(draw_field)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: draw_field.configure(
                scrollregion=draw_field.bbox("all")
            )
        )
        draw_field.create_window((0, 0), window=scrollable_frame, anchor="nw")
        draw_field.configure(yscrollcommand=scroll_bar.set)
        scroll_frame.grid(row=0, column=0)
        draw_field.grid(row = 0, column = 0, columnspan=2)
        scroll_bar.grid(ipady = 120)

        # Button frame
        button_frame = Frame(root)
        button_frame.grid(row=0, column=1, rowspan=2)
        button_font = font.Font(family='Tahoma', size=24)

        # Image Buttons
        image_button = Button(button_frame, text="images", font=button_font)
        image_button.grid()

        # Construct Buttons
        construct_button = Button(button_frame, text="construct", font=button_font)
        construct_button.grid()

        # Crossing Buttons
        crossing_button = Button(button_frame, text="crossings", font=button_font, command=lambda: cross.Start(
            protein))
        crossing_button.grid()

        # Sequence Frame
        seq_frame = Frame(root, highlightbackground="green", highlightthickness="2")
        seq_text = Text(seq_frame, width="151", height="45")
        seq_text.insert('1.0', self.seq)
        seq_text.grid()
        seq_text.tag_configure('tag-center', justify='left')
        seq_frame.grid(row=1, column=0)
        root.mainloop()

    def load_protein(self, name):
        new_prot = cs.ProteinSeq(name)
        new_prot.load_me()
        sequence_ph = new_prot.seq
        a = 0
        new_string = ""
        while (a + 150 < len(sequence_ph)):
            olda = a
            a = a + 150
            new_string = new_string + sequence_ph[olda:a] + "\n"
        new_string = new_string + sequence_ph[a:-1]
        self.seq = new_string


RegionWindow("POK2")
