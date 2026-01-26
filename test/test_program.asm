; Generated 6502 Assembly Code
; Processor: 6502

    processor 6502
    org $0600    ; Start program at $0600

start:
    LDX #$FF
    TXS          ; Initialize stack pointer

    ; var x = <expression>
    LDA #$0A      ; Load literal 10
    STA $10        ; Store to x

    ; var y = <expression>
    LDA #$05      ; Load literal 5
    STA $11        ; Store to y

    ; var result = <expression>
    LDA #$00      ; Load literal 0
    STA $12        ; Store to result

    ; result = <expression>
    LDA $10        ; Load x
    PHA             ; Save left operand
    LDA $11        ; Load y
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CLC
    ADC $FE         ; Add
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; if statement
    LDA $10        ; Load x
    PHA             ; Save left operand
    LDA $11        ; Load y
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE         ; Compare left with right
    BEQ GT_F0     ; Equal, return 0
    BCC GT_F0     ; left < right, return 0
    LDA #1          ; left > right
    JMP GT_E1
GT_F0:
    LDA #0          ; Not greater
GT_E1:
    CMP #0
    BEQ ELSE2    ; Jump to else if false

    ; result = <expression>
    LDA #$01      ; Load literal 1
    STA $12        ; Store to result

    JMP ENDIF3     ; Skip else branch

ELSE2:
    ; result = <expression>
    LDA #$00      ; Load literal 0
    STA $12        ; Store to result

ENDIF3:

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; var counter = <expression>
    LDA #$00      ; Load literal 0
    STA $13        ; Store to counter

WHILE4:
    ; while condition
    LDA $13        ; Load counter
    PHA             ; Save left operand
    LDA #$05      ; Load literal 5
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE         ; Compare left with right
    BCC LT_T6    ; Branch if left < right
    LDA #0          ; False
    JMP LT_E7
LT_T6:
    LDA #1          ; True
LT_E7:
    CMP #0
    BEQ ENDWHILE5      ; Exit loop if false

    ; counter++
    INC $13

    ; output(<value>)
    LDA $13        ; Load counter
    JSR output_routine

    JMP WHILE4    ; Loop back
ENDWHILE5:

DO8:
    ; do-while body
    ; x--
    DEC $10

    ; output(<value>)
    LDA $10        ; Load x
    JSR output_routine

    ; while condition
    LDA $10        ; Load x
    PHA             ; Save left operand
    LDA #$00      ; Load literal 0
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE         ; Compare left with right
    BEQ GT_F9     ; Equal, return 0
    BCC GT_F9     ; left < right, return 0
    LDA #1          ; left > right
    JMP GT_E10
GT_F9:
    LDA #0          ; Not greater
GT_E10:
    CMP #0
    BNE DO8    ; Loop if true

    ; var a = <expression>
    LDA #$0F      ; Load literal 15
    STA $14        ; Store to a

    ; var b = <expression>
    LDA #$07      ; Load literal 7
    STA $15        ; Store to b

    ; result = <expression>
    LDA $14        ; Load a
    PHA             ; Save left operand
    LDA $15        ; Load b
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    AND $FE         ; Bitwise AND
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $14        ; Load a
    PHA             ; Save left operand
    LDA $15        ; Load b
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    ORA $FE         ; Bitwise OR
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $14        ; Load a
    PHA             ; Save left operand
    LDA $15        ; Load b
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    EOR $FE         ; Bitwise XOR
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; var test1 = <expression>
    LDA #$01      ; Load literal 1
    STA $16        ; Store to test1

    ; var test2 = <expression>
    LDA #$00      ; Load literal 0
    STA $17        ; Store to test2

    ; result = <expression>
    LDA $16        ; Load test1
    PHA             ; Save left operand
    LDA $17        ; Load test2
    TAY             ; Save right in Y
    PLA             ; Get left
    CMP #0
    BEQ AND_F11   ; Left is false
    TYA             ; Check right
    CMP #0
    BEQ AND_F11   ; Right is false
    LDA #1          ; Both true
    JMP AND_E12
AND_F11:
    LDA #0          ; At least one false
AND_E12:
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $16        ; Load test1
    PHA             ; Save left operand
    LDA $17        ; Load test2
    TAY             ; Save right in Y
    PLA             ; Get left
    CMP #0
    BNE OR_T13    ; Left is true
    TYA             ; Check right
    CMP #0
    BNE OR_T13    ; Right is true
    JMP OR_F14
OR_T13:
    LDA #1          ; At least one true
    JMP OR_E15
OR_F14:
    LDA #0          ; Both false
OR_E15:
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $16        ; Load test1
    PHA             ; Save left operand
    LDA $17        ; Load test2
    TAY             ; Save right in Y
    PLA             ; Get left
    CMP #0
    BNE XOR_LT16
XOR_LF17:
    TYA
    CMP #0
    BEQ XOR_RF19  ; L=F, R=F -> F
    JMP XOR_RT18   ; L=F, R=T -> T
XOR_LT16:
    TYA
    CMP #0
    BEQ XOR_RT18   ; L=T, R=F -> T
    JMP XOR_RF19  ; L=T, R=T -> F
XOR_RT18:
    LDA #1
    JMP XOR_E20
XOR_RF19:
    LDA #0
XOR_E20:
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $14        ; Load a
    PHA             ; Save left operand
    LDA #$02      ; Load literal 2
    TAX             ; Shift count in X
    PLA             ; Get value
SHL21:
    CPX #0
    BEQ SHL_E22
    ASL             ; Shift left accumulator
    DEX
    JMP SHL21
SHL_E22:
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $15        ; Load b
    PHA             ; Save left operand
    LDA #$01      ; Load literal 1
    TAX             ; Shift count in X
    PLA             ; Get value
SHR23:
    CPX #0
    BEQ SHR_E24
    LSR             ; Shift right accumulator
    DEX
    JMP SHR23
SHR_E24:
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; x = <expression>
    LDA #$0C      ; Load literal 12
    STA $10        ; Store to x

    ; result = <expression>
    LDA $10        ; Load x
    EOR #$FF        ; One's complement
    CLC
    ADC #1          ; Two's complement (negate)
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine

    ; result = <expression>
    LDA $14        ; Load a
    EOR #$FF        ; Bitwise NOT
    STA $12        ; Store to result

    ; output(<value>)
    LDA $12        ; Load result
    JSR output_routine


    BRK          ; End program

; ==================== I/O Routines ====================

; Target: py65mon emulator
; Console output at $F001, input at $F004

output_routine:
    ; Output value in A as decimal number (0-255)
    ; Uses zero-page $FB-$FD for temporary storage
    STA $FB          ; Store number to output
    LDA #1
    STA $FD          ; Start suppressing leading zeros

    ; Output hundreds digit
    LDA $FB
    LDX #0           ; X will count hundreds
output_hundreds:
    CMP #100
    BCC output_hundreds_done
    SBC #100         ; Subtract 100 (carry is set)
    INX
    JMP output_hundreds
output_hundreds_done:
    STA $FB          ; Save remainder
    TXA
    BEQ skip_hundreds ; Skip if zero
    LDA #0
    STA $FD          ; Found non-zero, stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output hundreds digit
skip_hundreds:

    ; Output tens digit
    LDA $FB
    LDX #0           ; X will count tens
output_tens:
    CMP #10
    BCC output_tens_done
    SBC #10          ; Subtract 10 (carry is set)
    INX
    JMP output_tens
output_tens_done:
    STA $FB          ; Save remainder (ones digit)
    TXA
    BNE print_tens   ; Print if non-zero
    LDA $FD
    BNE skip_tens    ; Skip if still suppressing zeros
print_tens:
    LDA #0
    STA $FD          ; Stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output tens digit
skip_tens:

    ; Output ones digit (always output, even if zero)
    LDA $FB
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output ones digit

    ; Output newline
    LDA #10
    STA $F001
    RTS

input_routine:
    ; Read character from py65mon console input
    LDA $F004       ; Read from console input
    SEC
    SBC #48         ; Convert from ASCII to number
    RTS
