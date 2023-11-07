package org.example;

import com.itextpdf.text.pdf.*;
import com.itextpdf.text.*;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

import com.itextpdf.text.pdf.ColumnText;
import com.itextpdf.tool.xml.ElementHandler;
import com.itextpdf.tool.xml.Writable;
import com.itextpdf.tool.xml.XMLWorkerHelper;
import com.itextpdf.tool.xml.pipeline.WritableElement;

public class HeaderFooterPageEvent extends PdfPageEventHelper {

    Font ffont = new Font(Font.FontFamily.UNDEFINED, 15, Font.BOLD);
    PdfTemplate total;

    public void onOpenDocument(PdfWriter writer, Document document) {
        total = writer.getDirectContent().createTemplate(30, 16);
    }
    @Override
    public void onStartPage(PdfWriter writer, Document document) {
        try {
            //Add logo
            InputStream imageStream = Main.class.getResourceAsStream("/logo.jpg");
            Image logo = Image.getInstance(javax.imageio.ImageIO.read(imageStream), null);
            logo.scaleAbsolute((float) 85.6, (float) 62.27);
            logo.setAbsolutePosition(36, document.top());
            writer.getDirectContent().addImage(logo);

            // Create elements list
            ArrayList<Element> htmlElements = new ArrayList<>();

            // Read the HTML content
            InputStream htmlStream = Main.class.getResourceAsStream("/header.html");
            XMLWorkerHelper.getInstance().parseXHtml(new ElementHandler() {
                @Override
                public void add(final Writable writable) {
                    if (writable instanceof WritableElement) {
                        htmlElements.addAll(((WritableElement) writable).elements());
                    }
                }
            }, htmlStream, StandardCharsets.UTF_8);

            // Draw Header
            PdfContentByte cb = writer.getDirectContent();

            for (Element element : htmlElements) {
                try {
                    ColumnText ct = new ColumnText(cb);
                    ct.setSimpleColumn(document.left() +120f, document.top() + 100f, document.right(), document.top() -100f);
                    ct.addElement(element);
                    ct.go();
                } catch (DocumentException e) {
                    e.printStackTrace();
                }
            }

        } catch (Exception e) {
            throw new ExceptionConverter(e);
        }
    }

    public void onEndPage(PdfWriter writer, Document document) {
        PdfContentByte cb = writer.getDirectContent();

        // Footer text
        Phrase footer = new Phrase("Page " + writer.getPageNumber() + " of ", ffont);

        // Draw footer
        ColumnText.showTextAligned(cb, Element.ALIGN_CENTER,
                footer, (document.right() - document.left())/2 + document.leftMargin() , document.bottom() - 10, 0);

        cb.addTemplate(total, (document.right() - document.left())/2 + document.leftMargin() + 40 , document.bottom() - 11);
    }

    public void onCloseDocument(PdfWriter writer, Document document) {
        // Draw total count
        ColumnText.showTextAligned(total, Element.ALIGN_CENTER,
                new Phrase(String.valueOf(writer.getPageNumber()), ffont), 5, 1, 0);
    }
}
