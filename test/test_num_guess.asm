; Generated 6502 Assembly Code
; Processor: 6502

    processor 6502
    org $0600    ; Start program at $0600

start:
    LDX #$FF
    TXS          ; Initialize stack pointer

    ; var ans = <expression>
    LDA #$4D      ; Load literal 77
    STA $10        ; Store to ans

    ; var guess = <expression>
    LDA #$00      ; Load literal 0
    STA $11        ; Store to guess

WHILE0:
    ; while condition
    LDA $11        ; Load guess
    PHA             ; Save left operand
    LDA $10        ; Load ans
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE
    BNE NE_T2
    LDA #0          ; Equal
    JMP NE_E3
NE_T2:
    LDA #1          ; Not equal
NE_E3:
    CMP #0
    BEQ ENDWHILE1      ; Exit loop if false

    ; guess = <expression>
    ; input() function call
    JSR input_routine
    STA $11        ; Store to guess

    ; if statement
    LDA $11        ; Load guess
    PHA             ; Save left operand
    LDA $10        ; Load ans
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE         ; Compare left with right
    BCC LT_T4    ; Branch if left < right
    LDA #0          ; False
    JMP LT_E5
LT_T4:
    LDA #1          ; True
LT_E5:
    CMP #0
    BEQ ELSE6    ; Jump to else if false

    ; output(<value>)
    LDA #$00      ; Load literal 0
    JSR output_routine

    JMP ENDIF7     ; Skip else branch

ELSE6:
    ; if statement
    LDA $11        ; Load guess
    PHA             ; Save left operand
    LDA $10        ; Load ans
    STA $FE         ; Save right operand
    PLA             ; Restore left operand
    CMP $FE         ; Compare left with right
    BEQ GT_F8     ; Equal, return 0
    BCC GT_F8     ; left < right, return 0
    LDA #1          ; left > right
    JMP GT_E9
GT_F8:
    LDA #0          ; Not greater
GT_E9:
    CMP #0
    BEQ ELSE10    ; Jump to else if false

    ; output(<value>)
    LDA #$02      ; Load literal 2
    JSR output_routine

    JMP ENDIF11     ; Skip else branch

ELSE10:
ENDIF11:

ENDIF7:

    JMP WHILE0    ; Loop back
ENDWHILE1:

    ; output(<value>)
    LDA #$01      ; Load literal 1
    JSR output_routine


    BRK          ; End program

; ==================== I/O Routines ====================

; Target: py65mon emulator
; Console output at $F001, blocking input at $F005

output_routine:
    ; Output value in A as decimal number (0-255)
    ; Uses zero-page $FB-$FD for temporary storage
    ; Algorithm: Repeatedly divide by 100, 10 to extract digits
    ; Suppresses leading zeros (e.g., 5 prints as '5' not '005')
    STA $FB          ; Store number to output
    LDA #1
    STA $FD          ; Start suppressing leading zeros

    ; ===== Output hundreds digit =====
    ; Extract hundreds by repeated subtraction
    ; Example: 234 → subtract 100 twice → hundreds = 2
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
    BEQ skip_hundreds ; Skip if zero (suppress leading zero)
    LDA #0
    STA $FD          ; Found non-zero, stop suppressing
    TXA
    CLC
    ADC #48          ; Convert to ASCII ('0' = 48)
    STA $F001        ; Output hundreds digit
skip_hundreds:

    ; ===== Output tens digit =====
    ; Extract tens from remainder by repeated subtraction
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

    ; ===== Output ones digit =====
    ; Always output ones digit, even if zero (e.g., for '0', '10', '100')
    LDA $FB
    CLC
    ADC #48          ; Convert to ASCII
    STA $F001        ; Output ones digit

    ; Output newline for readability
    LDA #10
    STA $F001
    RTS

input_routine:
    ; Read multi-digit number from console until Enter
    ; Reads ASCII digits and converts to binary (0-255 max)
    ; Uses zero-page $FA for accumulating result
    ; Algorithm: For each digit, multiply result by 10 and add digit
    ; Example: '123' → 0*10+1=1, 1*10+2=12, 12*10+3=123
    LDA #0
    STA $FA         ; Initialize result to 0

input_loop:
    ; ===== Wait for next character =====
input_wait:
    LDA $F004       ; Poll for input (non-blocking)
    BEQ input_wait  ; Keep waiting if no key pressed

    ; ===== Check for Enter key =====
    ; Enter terminates input
    CMP #10
    BEQ input_done  ; If Enter (LF), we're done
    CMP #13
    BEQ input_done  ; If Enter (CR), we're done

    ; ===== Convert ASCII digit to number =====
    ; ASCII '0'-'9' are 48-57, so subtract 48
    SEC
    SBC #48
    STA $FE         ; Store new digit in $FE

    ; ===== Multiply current result by 10 =====
    ; Uses bit shifts: result * 10 = (result * 2 * 5) = (result << 1) * 5
    ; And: result * 5 = (result << 2) + result
    ; Combined: result * 10 = ((result << 2) + result) << 1
    LDA $FA         ; Load current result
    STA $FD         ; Save copy
    ASL             ; result * 2
    ASL             ; result * 4
    CLC
    ADC $FD         ; result * 4 + result * 1 = result * 5
    ASL             ; result * 10
    CLC
    ADC $FE         ; Add new digit
    STA $FA         ; Store updated result

    JMP input_loop  ; Read next character

input_done:
    LDA $FA         ; Load final result into A
    RTS
