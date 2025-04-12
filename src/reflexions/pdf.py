# from __future__ import annotations

# import reflex as rx


# def pdf_preview() -> rx.Component:
#     return rx.box(
#         rx.heading("PDF Preview", size="4", margin_bottom="1em"),
#         rx.cond(
#             State.base64_pdf != "",
#             rx.html(
#                 f"""
#                 <iframe
#                     src="data:application/pdf;base64,{State.base64_pdf}"
#                     width="100%"
#                     height="600px"
#                     style="border: none; border-radius: 8px;">
#                 </iframe>
#                 """
#             ),
#             rx.text("No PDF uploaded yet", color="red"),
#         ),
#         width="100%",
#         margin_top="1em",
#         border_radius="md",
#         overflow="hidden",
#     )
